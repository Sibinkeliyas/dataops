import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Ticket, Activity, Bell, Database, BarChart2, Brain, Cog } from 'lucide-react';

const Dashboard = () => {
  const userName = "John Doe"; // This should be dynamically fetched from user data
  const currentDate = new Date().toLocaleDateString();
  const currentTime = new Date().toLocaleTimeString();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-blue-100 p-6 rounded-lg mb-8">
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-2">Welcome back, {userName}!</h1>
        <p className="text-lg md:text-xl">{currentDate} - {currentTime}</p>
        <p className="text-sm md:text-base mt-2">Tip: Check out our new data quality dashboard for real-time insights!</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-6">
        {/* Existing cards */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Ticket className="mr-2" /> My Tickets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Open: 3</p>
            <p>In Progress: 2</p>
            <p>Resolved: 5</p>
            <Button className="mt-4">View All Tickets</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="mr-2" /> Pipeline Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Total Pipelines: 10</p>
            <p>Successful Runs Today: 8</p>
            <p>Failed Runs Today: 1</p>
            <Button className="mt-4">View Pipeline Details</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bell className="mr-2" /> Recent Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul>
              <li>Critical: Data pipeline failure</li>
              <li>Warning: Low storage space</li>
              <li>Info: New dataset available</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="mr-2" /> Data Catalog Shortcuts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul>
              <li>Sales Data 2023</li>
              <li>Customer Feedback</li>
              <li>Product Inventory</li>
            </ul>
            <Button className="mt-4">Open Data Catalog</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart2 className="mr-2" /> BI Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul>
              <li>Monthly Sales Dashboard</li>
              <li>Customer Retention Analysis</li>
              <li>Product Performance</li>
            </ul>
            <Button className="mt-4">View All Reports</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="mr-2" /> Machine Learning Projects
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul>
              <li>Sales Prediction Model (Accuracy: 92%)</li>
              <li>Customer Churn Analysis (In Progress)</li>
              <li>Image Recognition for QC (Deployed)</li>
            </ul>
            <Button className="mt-4">Manage ML Projects</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Cog className="mr-2" /> Data Engineering Tasks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul>
              <li>Data Ingestion for Sales Data (Completed)</li>
              <li>ETL Pipeline Optimization (In Progress)</li>
              <li>Data Quality Check (Scheduled)</li>
            </ul>
            <Button className="mt-4">View Task Details</Button>
          </CardContent>
        </Card>

        {/* Add more cards for ultra-wide screens */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="mr-2" /> Data Quality
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Overall Score: 95%</p>
            <p>Issues Detected: 2</p>
            <Button className="mt-4">View Details</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="mr-2" /> System Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>CPU Usage: 65%</p>
            <p>Memory: 8.2GB / 16GB</p>
            <Button className="mt-4">Monitor Resources</Button>
          </CardContent>
        </Card>
      </div>

      {/* Announcements section */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Announcements and Updates</h2>
        <Card>
          <CardContent>
            <h3 className="font-semibold">Company News</h3>
            <p>allnex launches new data-driven initiative to improve product quality.</p>
            <h3 className="font-semibold mt-4">Scheduled Maintenance</h3>
            <p>System upgrade planned for this weekend. Some services may be unavailable.</p>
            <h3 className="font-semibold mt-4">New Features</h3>
            <p>Introducing advanced data lineage tracking in our Data Catalog. <Button variant="link">Learn More</Button></p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
