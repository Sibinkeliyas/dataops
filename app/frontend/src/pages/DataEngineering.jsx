import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Database, GitBranch, BarChart2, CheckCircle, Clock, Users, Shield } from 'lucide-react';

const DataEngineering = () => {
  const sections = [
    { title: 'Databricks Workspace', icon: Database, path: '/data-engineering/databricks' },
    { title: 'ETL Pipelines', icon: GitBranch, path: '/data-engineering/etl-pipelines' },
    { title: 'Data Transformations', icon: BarChart2, path: '/data-engineering/transformations' },
    { title: 'Data Quality and Validation', icon: CheckCircle, path: '/data-engineering/data-quality' },
    { title: 'Job Scheduling', icon: Clock, path: '/data-engineering/job-scheduling' },
    { title: 'Collaboration Tools', icon: Users, path: '/data-engineering/collaboration' },
    { title: 'Data Governance and Compliance', icon: Shield, path: '/data-engineering/governance' },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <nav className="text-sm mb-4" aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          <li className="flex items-center">
            <Link to="/" className="text-blue-500">Home</Link>
            <span className="mx-2">/</span>
          </li>
          <li className="flex items-center">
            Data Engineering
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl font-bold mb-6">Data Engineering</h1>
      <p className="text-lg mb-8">
        The Data Engineering section is the backbone of the Mithril platform, empowering data engineers to design, develop, and manage data pipelines and transformations that process and prepare data for analytics and AI. Leveraging the power of Databricks, this section provides robust tools for handling large-scale data processing with efficiency and scalability.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.map((section, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="flex items-center">
                <section.icon className="mr-2 text-primary-500" /> {section.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4">Access tools and features for {section.title.toLowerCase()}.</p>
              <Link to={section.path}>
                <Button className="w-full">Explore {section.title}</Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default DataEngineering;