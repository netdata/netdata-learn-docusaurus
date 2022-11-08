# Imports
import argparse
import copy
import glob
import itertools
import os
import pathlib
import re
import shutil
import errno
import git

dryRun = False

restFilesDictionary = {}
toPublish = {}
markdownFiles = []
docsPrefix = "docs"
TEMP_FOLDER = "ingest-temp-folder"
defaultRepos = {
    "netdata":
        {
            "owner": "netdata",
            "branch": "master",
        },
    "go.d.plugin":
        {
            "owner": "netdata",
            "branch": "master",
        },
    ".github":
        {
            "owner": "netdata",
            "branch": "main",
        },
    "agent-service-discovery":
        {
            "owner": "netdata",
            "branch": "master",
        }
}


# defaultRepoInaStr = " ".join(defaultRepo)
# print(defaultRepoInaStr)

# Will come back to this once we have a concrete picture of the script
# if sys.argv[1] == "dry-run":
#     print("--- DRY RUN ---\n")
#     dry_run = True

def unSafeCleanUpFolders(folderToDelete):
    print("Try to clean up the folder: ", folderToDelete)
    try:
        shutil.rmtree(folderToDelete)
        print("Done")
    except Exception as e:
        print("Couldn't delete the folder due to the exception: \n", e)


def safeCleanUpFolders():
    pass


def renameReadmes(fileArray):
    """
    In this function we will get the whole list of files,
    search for README named files, and rename them in accordance to their parent dir name.
    After we rename, we need to update the list entry.
    """
    # TODO think of a way of not renaming the unpublished files (?) this will affect only the README s
    counter = 0
    for filename in fileArray:
        if filename.__contains__("README"):
            # Get the path without the filename
            filename = pathlib.Path(filename)
            # And then from that take the last dir, which is the name we want to rename to, add a needed "/" and the
            # ".md"
            newPath = os.path.dirname(filename) + "/" + os.path.basename(filename.parent.__str__()[1:]) + ".md"

            os.rename(filename, newPath)
            fileArray[counter] = newPath
        counter += 1


def moveDoc(src, dest):
    """REQUIRES:
    In the oldFilePath the metadata:
    learn_topic_type: e.g. Concepts
    learn_rel_path: e.g /agent/ <- the folder inside the Concepts directory
    """
    # Get the path
    try:
        shutil.copy(src, dest)
    except IOError as e:
        # ENOENT(2): file does not exist, raised also on missing dest parent dir
        if e.errno != errno.ENOENT:
            raise
        # try creating parent directories
        os.makedirs(os.path.dirname(dest))
        shutil.copy(src, dest)


def cloneRepo(owner, repo, branch, depth, prefixFolder):
    try:
        outputFolder = prefixFolder + repo
        # print("DEBUG", outputFolder)
        git.Git().clone("https://github.com/{}/{}.git".format(owner, repo), outputFolder, depth=depth, branch=branch)
        return "Cloned the {} branch from {} repo (owner: {})".format(branch, repo, owner)
    except Exception as e:
        return (
            "Couldn't clone the {} branch from {} repo (owner: {}) \n Exception {} raised".format(branch, repo, owner,
                                                                                                  e))

def createMDXPathFromMetdata(metadata):
    finalFile = ' '.join((metadata["sidebar_label"].replace("/", " ").replace(")", " ").replace(",", " ").replace("(", " ")).split())
    return("{}/{}/{}.mdx".format(docsPrefix, \
                    metadata["learn_rel_path"], \
                    finalFile.replace(" ", "-")).lower().replace(" ", "-").replace("//","/"))
 


def fetchMarkdownFromRepo(outputFolder):
    return glob.glob(outputFolder + '/**/*.md*', recursive=True)


def readMetadataFromDoc(pathToPath):
    """
    Taking a path of a file as input
    Identify the area with pattern " <!-- ...multiline string -->" and  converts them
    to a dictionary of key:value pairs
    """
    metadataDictionary = {}
    with open(pathToPath, "r+") as fd:
        rawText = "".join(fd.readlines())
        pattern = r"(<!--\n)((.|\n)*)(\n-->)"
        matchGroup = re.search(pattern, rawText)
        if matchGroup:
            rawMetadata = matchGroup[2]
            listMetadata = rawMetadata.split("\n")
            while listMetadata:
                line = listMetadata.pop(0)
                splitInKeywords = line.split(": ")
                key = splitInKeywords[0]
                value = splitInKeywords[1]
                # If it's a multiline string
                while listMetadata and len(listMetadata[0].split(": ")) <= 1:
                    line = listMetadata.pop(0)
                    value = value + line.lstrip(' ')
                value = value.strip("\"")
                metadataDictionary[key] = value.lstrip('>-')
    return(metadataDictionary)


def sanitizePage(path):
    # Open the file for reading
    file = open(path, "r")
    body = file.read()
    file.close()

    # Replace the metadata with comments
    body = body.replace("<!--", "---")
    body = body.replace("-->", "---")

    # The list with the lines that will be written in the file
    output = []

    # For each line of the file I read
    for line in body.splitlines():
        # If the line isn't an H1 title, and it isn't an analytics pixel, append it to the output list
        if not line.startswith("# ") and not line.startswith("[![analytics]"):
            output.append(line + "\n")

    # TODO remove github badges

    # Open the file for overwriting, we are going to write the output list in the file
    file = open(path, "w")
    file.seek(0)
    file.writelines(output)


def fixMovedLinks(path, dict):
    # Open the file for reading
    file = open(path, "r")
    body = file.read()
    file.close()
    output = []

    # For every line in the file we are going to search for urls,
    # and check the dictionary for the relative path of Learn.
    for line in body.splitlines():
        if re.search("\]\((.*?)\)", line):
            # Find all the links inside that line
            urls = re.findall("\]\((.*?)\)", line)

            for url in urls:
                replaceString = url
                # If the URL is a GitHub one
                if not (url.startswith("#") or url.startswith("http") or url.startswith("https://learn.netdata.cloud")):
                    # The URLs we care about are the ones that are relative to their repo, so we add a dot to make
                    # them match the keys inside the dictionary
                    key = "." + url

                    # If it is indeed a key inside the dictionary
                    if key in dict.keys():
                        metadata = dict.get(key)
                        replaceString = metadata.get("newLearnPath").split("..")[1]
                # Remove the .md
                line = line.replace(url, replaceString.split('.md')[0])
        output.append(line + "\n")

    file = open(path, "w")
    file.seek(0)
    file.writelines(output)
    file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest docs from multiple repositories')

    parser.add_argument(
        '--repos',
        default=[],
        nargs='+',
        help='Choose specific repo you want ingest, if not set, defaults ingested'
    )

    parser.add_argument(
        "-d", "--dry-run",
        help="Don't save a file with the output.",
        action="store_true",
    )

    listOfReposInStr = []
    # netdata/netdata:branch tkatsoulas/go.d.plugin:mybranch
    kArgs = parser.parse_args()._get_kwargs()
    for x in kArgs:
        if x[0] == "repos":
            listOfReposInStr = x[1]
        if x[0] == "dryRun":
            print(x[1])
            dryRun = x[1]

    if len(listOfReposInStr) > 0:
        for repoStr in listOfReposInStr:
            try:
                _temp = repoStr.split("/")
                owner, repo, branch = [_temp[0]] + (_temp[1].split(":"))
                defaultRepos[repo]["owner"] = owner
                defaultRepos[repo]["branch"] = branch
            except(TypeError, ValueError):
                print("You specified a wrong format in at least one of the repos you want to ingest")
                parser.print_usage()
                exit(-1)
            except KeyError:
                print(repo)
                print("The repo you specified in not in predefined repos")
                print(defaultRepos.keys())
                parser.print_usage()
                exit(-1)
            except Exception as e:
                print("Unknown error in parsing", e)

    '''
    Clean up old clones into a temp dir
    '''
    unSafeCleanUpFolders(TEMP_FOLDER)

    print("Creating a temp directory \"temp_clones\"")
    try:
        os.mkdir(TEMP_FOLDER)
    except FileExistsError:
        print("Folder already exists")

    '''Clone all the predefined repos'''
    for key in defaultRepos.keys():
        print(cloneRepo(defaultRepos[key]["owner"], key, defaultRepos[key]["branch"], 1, TEMP_FOLDER + "/"))
    # This line is useful only during the rework
    print(cloneRepo("netdata", "learn", "rework-learn", 1, TEMP_FOLDER + "/"))
    # We fetch the markdown files from the repositories
    markdownFiles = list(itertools.chain(fetchMarkdownFromRepo(TEMP_FOLDER + "/netdata"),
                                         fetchMarkdownFromRepo(TEMP_FOLDER + "/go.d.plugin"),
                                         fetchMarkdownFromRepo(TEMP_FOLDER + "/github"),
                                         # This line is useful only during the rework
                                         fetchMarkdownFromRepo(TEMP_FOLDER + "/learn")))

    print("Files detected: ", len(markdownFiles))
    print("Gathering Learn files...")
    # After this we need to keep only the files that have metadata, so we will fetch metadata for everything and keep
    # the entries that have populated dictionaries
    reducedMarkdownFiles = []
    for md in markdownFiles:
        metadata = readMetadataFromDoc(md)
        # Check to see if the dictionary returned is empty
        if len(metadata)>0:
            reducedMarkdownFiles.append(md)
            if "learn_status" in metadata.keys():
                if metadata["learn_status"] == "Published":
                    try:
                        toPublish[md] = {
                            "metadata": str(metadata),
                            "learnPath": str(createMDXPathFromMetdata(metadata)),
                            "ingestedRepo": str(md.split("/",2)[1])
                        }
                    except:
                        print("File {} doesnt container key-value {}".format(md, KeyError))
            else:
                restFilesDictionary[md] = {
                    "metadata": str(metadata),
                    "learnPath": str("docs/_archive/_{}".format(md)),
                    "ingestedRepo": str(md.split("/", 2)[1])
                }

        del metadata
    # we update the list only with the files that are destined for Learn



    #identify published documents:q
    print("  Found Learn files: ", len(markdownFiles))
    for file in toPublish:
        moveDoc(file, toPublish[file]["learnPath"])
        sanitizePage(toPublish[file]["learnPath"])
    for file in restFilesDictionary:
        pass
        #moveDoc(file, restFilesDictionary[file]["learnPath"])

    """
    print("  Renaming README.md files...")
    renameReadmes(markdownFiles)

    print("Done.")

    # METADATA

    print("Reading the metadata for each file...")

    print("Done.")
    for k,v in filesDictionary.items():
        print("File ", k )
        print("Has metadata", v)
        print("")

    # FILE MOVING
    '''
    print("Moving files...")

    # TODO the dict needs to be filename -> oldPath newPath metadata

    # Then we need to sanitize the page and move it to the correct path, if it doesn't have a path for now we continue
    # on, so it doesn't get moved anywhere

    learnFilesDict = copy.copy(filesDictionary)
    for md in filesDictionary:
        sanitizePage(md)
        # If I have the metadata needed ot build a path, move the file to the correct destination
        if "learn_rel_path" in filesDictionary.get(md).keys() and "learn_topic_type" in filesDictionary.get(
                md).keys() and "learn_status" in \
                filesDictionary.get(md).keys():
            if filesDictionary.get(md).get("learn_status") == "published":
                changePath(md,
                           docsPrefix +
                           filesDictionary.get(md).get("learn_topic_type").strip("\n") +
                           filesDictionary.get(md).get("learn_rel_path").strip("\n") +
                           os.path.basename(md))

            elif filesDictionary.get(md).get("learn_status") == "unpublished":
                changePath(md, docsPrefix + "/_unpublished/unpublished/" + md)
                learnFilesDict.pop(md)
            elif filesDictionary.get(md).get("learn_status") == "deprecated":
                changePath(md, docsPrefix + "/_unpublished/deprecated/" + md)
                learnFilesDict.pop(md)
            else:
                changePath(md, docsPrefix + "/_unpublished/wrong_status/" + md)
                learnFilesDict.pop(md)

        else:
            changePath(md, docsPrefix + "/_unpublished/no_status/" + md)
            learnFilesDict.pop(md)
    print("Done")

    # FIX LINKS

    print("Fixing github links...")

    # After the moving, we have a new metadata, called newLearnPath, and we utilize that to fix links that were
    # pointing to GitHub relative paths
    for md in learnFilesDict:
        if "newLearnPath" in learnFilesDict.get(md).keys():
            fixMovedLinks(learnFilesDict.get(md)["newLearnPath"], learnFilesDict)

    print("Done.")
    """
print("OPERATION FINISHED")
