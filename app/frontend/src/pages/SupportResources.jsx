import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, HelpCircle, MessageSquare, Mail, BookOpen } from 'lucide-react';
import HelpCenter from '../components/HelpCenter';
import ContactSupport from '../components/ContactSupport';
import TrainingTutorials from '../components/TrainingTutorials';

const SupportResources = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Support & Resources</h1>
      <p className="text-lg mb-8">Access comprehensive help, documentation, and support for the Mithril Data Platform. Our resources are designed to empower you in leveraging the full potential of our tools.</p>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-2xl">Quick Access</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <HelpCircle className="text-primary-500" />
            <span>FAQs</span>
          </div>
          <div className="flex items-center space-x-2">
            <MessageSquare className="text-primary-500" />
            <span>Community Forums</span>
          </div>
          <div className="flex items-center space-x-2">
            <BookOpen className="text-primary-500" />
            <span>Documentation</span>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="help-center" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="help-center">Help Center</TabsTrigger>
          <TabsTrigger value="contact-support">Contact Support</TabsTrigger>
          <TabsTrigger value="training-tutorials">Training & Tutorials</TabsTrigger>
        </TabsList>

        <TabsContent value="help-center">
          <Card>
            <CardHeader>
              <CardTitle>Help Center</CardTitle>
            </CardHeader>
            <CardContent>
              <HelpCenter />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contact-support">
          <Card>
            <CardHeader>
              <CardTitle>Contact Support</CardTitle>
            </CardHeader>
            <CardContent>
              <ContactSupport />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="training-tutorials">
          <Card>
            <CardHeader>
              <CardTitle>Training & Tutorials</CardTitle>
            </CardHeader>
            <CardContent>
              <TrainingTutorials />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SupportResources;