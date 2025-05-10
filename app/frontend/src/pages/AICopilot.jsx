import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageSquare, Bot, Cpu } from 'lucide-react';

const AICopilot = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">AI Copilot</h1>
      <p className="text-lg mb-8">Interact with data through natural language queries and automate complex tasks.</p>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageSquare className="mr-2" /> AI Assistant
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex mb-4">
            <Input placeholder="Ask a question or request a task..." className="mr-2" />
            <Button>Send</Button>
          </div>
          <div className="bg-gray-100 p-4 rounded-md">
            <p className="text-gray-600">AI responses will appear here...</p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bot className="mr-2" /> Task Automation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Automate complex data tasks using AI-powered workflows.</p>
            <Button className="mt-4">Create Workflow</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Cpu className="mr-2" /> AI Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Get AI-generated insights and recommendations from your data.</p>
            <Button className="mt-4">Generate Insights</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AICopilot;