import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const GetStartedSection = () => {
  return (
    <section className="mb-12">
      <h3 className="text-2xl font-bold text-white mb-6">Get Started Today</h3>
      <Card className="bg-white bg-opacity-90">
        <CardHeader>
          <CardTitle>Embark on a Journey of Innovation</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside mb-4">
            <li>Webinars and Workshops: Participate in sessions covering data fundamentals to advanced analytics.</li>
            <li>Tutorials and Guides: Access step-by-step instructions for navigating Mithril, Power BI, Microsoft Fabric, and Azure AI Studio.</li>
            <li>Community Engagement: Connect with colleagues, share knowledge, and collaborate on projects.</li>
          </ul>
          <Button className="w-full">Visit the Learning Center</Button>
        </CardContent>
      </Card>
    </section>
  );
};

export default GetStartedSection;