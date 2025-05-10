import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Glasses, BarChart2, CheckCircle, Download, FileText, Phone } from 'lucide-react';

const ARSolutions = () => {
  const arTools = [
    {
      name: "DataViz AR",
      description: "Visualize complex data sets in 3D space",
      devices: "HoloLens 2, Magic Leap 2, iOS/Android devices",
    },
    {
      name: "QualityCheck AR",
      description: "AR-assisted quality control for manufacturing",
      devices: "HoloLens 2, Android industrial tablets",
    },
    {
      name: "TrainingSimulator AR",
      description: "Interactive AR training for new employees",
      devices: "All AR-capable smartphones and tablets",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Augmented Reality (AR) Solutions</h1>
      <p className="text-lg mb-8">Visualize data analytics in real-time and improve quality control with AR.</p>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">AR Applications</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {arTools.map((tool, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Glasses className="mr-2 text-primary-500" /> {tool.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-2">{tool.description}</p>
                <p className="text-sm text-gray-600 mb-4">Supported Devices: {tool.devices}</p>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" className="flex items-center">
                    <Download className="mr-1 h-4 w-4" /> Download App
                  </Button>
                  <Button size="sm" variant="outline" className="flex items-center">
                    <FileText className="mr-1 h-4 w-4" /> User Guide
                  </Button>
                  <Button size="sm" variant="secondary" className="flex items-center">
                    <Phone className="mr-1 h-4 w-4" /> Request Demo
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">AR Implementation Guides</h2>
        <Card>
          <CardHeader>
            <CardTitle>Getting Started with AR</CardTitle>
          </CardHeader>
          <CardContent>
            <h3 className="font-semibold mb-2">Hardware Requirements</h3>
            <ul className="list-disc list-inside mb-4">
              <li>AR-capable device (HoloLens 2, Magic Leap 2, or compatible smartphone/tablet)</li>
              <li>Stable internet connection for real-time data streaming</li>
              <li>Optional: AR markers or QR codes for environment mapping</li>
            </ul>

            <h3 className="font-semibold mb-2">Installation Steps</h3>
            <ol className="list-decimal list-inside mb-4">
              <li>Download the appropriate AR application for your device</li>
              <li>Install and launch the application</li>
              <li>Follow the on-screen instructions for device calibration</li>
              <li>Connect to your Mithril Data Platform account</li>
              <li>Start exploring your data in AR!</li>
            </ol>

            <h3 className="font-semibold mb-2">Best Practices</h3>
            <ul className="list-disc list-inside">
              <li>Ensure a well-lit environment for optimal AR performance</li>
              <li>Regularly update your AR application for the latest features</li>
              <li>Use gestures and voice commands for efficient interaction</li>
              <li>Collaborate with team members using multi-user AR sessions</li>
              <li>Integrate AR insights into your regular workflow for maximum benefit</li>
            </ul>
          </CardContent>
        </Card>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">Core AR Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Glasses className="mr-2 text-primary-500" /> AR Visualization
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p>Experience data insights through immersive AR visualizations.</p>
              <Button className="mt-4">Launch AR View</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart2 className="mr-2 text-primary-500" /> Real-time Analytics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p>View and interact with real-time data analytics in AR.</p>
              <Button className="mt-4">Start Real-time Feed</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CheckCircle className="mr-2 text-primary-500" /> Quality Control
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p>Enhance quality control processes with AR-assisted inspections.</p>
              <Button className="mt-4">QC Checklist</Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default ARSolutions;