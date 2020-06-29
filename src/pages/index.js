import React from 'react';
import clsx from 'clsx';
import SVG from 'react-inlinesvg';

import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './styles.module.scss';
import { FiBox, FiServer, FiSliders, FiActivity, FiCpu, FiHome, FiMonitor, FiGrid, FiHardDrive, FiLock } from "react-icons/fi";

const docs = [
  {
    title: <>Getting started guide</>,
    href: 'docs/agent/getting-started',
    description: (
      <>
        Configure metrics retention, build streaming connections, collect metrics 
        from custom apps, create custom dashboards, and much more.
      </>
    ),
  },
  {
    title: <>Configuration</>,
    href: 'docs/agent/configuration-guide',
    description: (
      <>
        Use Netdata’s expansive customization possibilities to suit any service, any system, and any infrastructure.
      </>
    ),
  },
  {
    title: <>Collect metrics</>,
    href: 'docs/agent/collectors',
    description: (
      <>
        Add more charts to Netdata via its intelligent auto-detection of popular web servers, databases, mail servers, security apps, and dozens more.
      </>
    ),
  },
  {
    title: <>Health monitoring</>,
    href: 'docs/agent/health',
    description: (
      <>
        Tune existing alarms or create new ones, and enable any number of notification systems based on roles and severity.
      </>
    ),
  },
  {
    title: <>Netdata Cloud</>,
    href: 'docs/cloud',
    description: (
      <>
        Learn how to view real-time, distributed health monitoring and performance troubleshooting data for all your systems in one place.
      </>
    ),
  },
  {
    title: <>Custom dashboards</>,
    href: 'docs/agent/web/gui/custom',
    description: (
      <>
        Build bespoke dashboards with simple HTML and JavaScript to put all of your most important metrics in one easy-to-understand place.
      </>
    ),
  },
];

function DocBox({title, href, description}) {
  return (
    <Link to={useBaseUrl(href)} className={clsx('col col--4', styles.docBox)}>
      <h3>{title}</h3>
      <p>{description}</p>
    </Link>
  );
}

function StepByStepLink({icon, title, href}) {
  return (
    <Link 
      className={styles.stepByStepLink}
      to={useBaseUrl(href)}>
      <div className={styles.stepByStepIcon}>{icon}</div>
      {title}
    </Link>
  )
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;

  return (
    <Layout
      title={`All your monitoring education in one place. ${siteConfig.title}`}
      description="Learn alongside thousands of others who want to discover deeper insights about their systems and applications with Netdata's real-time health monitoring and performance troubleshooting toolkit.">
      <header className={clsx(styles.hero)}>
        <div className={clsx('container')}>
          <div className={clsx('row')}>
            <div 
              className={clsx(
                'col col--6',
                styles.heroText
              )}>
              <span>Learn @ Netdata</span>
              <h1 className={styles.heroTagline}>
                All your monitoring education in one place.
              </h1>
              <p className={styles.heroSubHead}>
                Learn alongside thousands of others who want to discover deeper insights about 
                their systems and applications with Netdata's real-time health monitoring and 
                performance troubleshooting toolkit.
              </p>
              <div className={styles.buttons}>
                <Link
                  className={clsx(
                    'button button--lg',
                    styles.getStarted,
                  )}
                  to={useBaseUrl('#installation')}>
                  Get Netdata
                </Link>
                <Link
                  className={clsx(
                    'button button--secondary button--lg',
                    styles.getStarted,
                  )}
                  to={useBaseUrl('docs/agent')}>
                  Read Agent docs
                </Link>
              </div>
            </div>
            <div className={clsx('col col--6', styles.heroImageContainer)}>
              <SVG 
                className={clsx(
                  styles.heroImage
                )} 
                src="img/index/hero.svg"
                alt="Netdata Learn: All your monitoring education in one place" 
              />
            </div>
          </div>
        </div>
      </header>
      <main>
        <section className={styles.stepByStep}>
          <div className={clsx('container')}>
            <div className={clsx('row row--center')}>
              <div className={clsx('col col--12')}>
                <h2>Learn Netdata step-by-step</h2>
              </div>
              <div className={clsx('col col--4')}>
                <p>Take a guided tour through Netdata's core features, including its famous dashboard, creating new alarms, and collecting metrics from your favorite services and applications.</p>
                <p>Ten easy-to-parse parts designed for beginners&mdash;perfect first experience for those who want to get started with monitoring and troubleshooting.</p>
              </div>
              <div className={clsx('col col--4', styles.stepByStepLinks)}>
                <StepByStepLink
                  href="guides/step-by-step/step-01"
                  icon={<FiBox />}
                  title="Netdata's building blocks"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-02"
                  icon={<FiHome />}
                  title="Get to know Netdata's dashboard"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-03"
                  icon={<FiServer />}
                  title="Monitor more than one system with Netdata"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-04"
                  icon={<FiSliders />}
                  title="The basics of configuring Netdata"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-05"
                  icon={<FiActivity />}
                  title="Health monitoring alarms and notifications"
                />
              </div>
              <div className={clsx('col col--4', styles.stepByStepLinks)}>
                <StepByStepLink
                  href="guides/step-by-step/step-06"
                  icon={<FiCpu />}
                  title="Collect metrics from more services and apps"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-07"
                  icon={<FiMonitor />}
                  title="Netdata’s dashboard in depth"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-08"
                  icon={<FiGrid />}
                  title="Building your first custom dashboard"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-09"
                  icon={<FiHardDrive />}
                  title="Long-term metrics storage"
                />
                <StepByStepLink
                  href="guides/step-by-step/step-10"
                  icon={<FiLock />}
                  title="Set up a proxy"
                />
              </div>
            </div>
          </div>
        </section>
        <section className={styles.docs}>
          <div className={clsx('container')}>
            <div className={clsx('row')}>
              {docs.map((props, idx) => (
                <DocBox key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

export default Home;
