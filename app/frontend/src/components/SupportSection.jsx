import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const SupportSection = () => {
  return (
    <section className="mb-12">
      <h3 className="text-2xl font-bold text-white mb-6">Support and Resources</h3>
      <Card className="bg-white bg-opacity-90">
        <CardHeader>
          <CardTitle>We're Here to Help</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside mb-4">
            <li>Help Center: Find FAQs, troubleshooting guides, and support documentation.</li>
            <li>Professional Assistance: Contact our support team for expert guidance.</li>
            <li>Continuous Improvement: Provide feedback to help us enhance the platform.</li>
          </ul>
          <Button className="w-full">Get Support</Button>
        </CardContent>
      </Card>
    </section>
  );
};

export default SupportSection;