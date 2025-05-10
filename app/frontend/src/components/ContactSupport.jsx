import React from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { MessageSquare, Mail, Upload, Phone } from 'lucide-react';

const ContactSupport = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Support Options</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center">
            <MessageSquare className="mr-2 text-primary-500" />
            <Button variant="link">Submit a Ticket</Button>
          </div>
          <div className="flex items-center">
            <MessageSquare className="mr-2 text-primary-500" />
            <Button variant="link">Live Chat (Business Hours)</Button>
          </div>
          <div className="flex items-center">
            <Mail className="mr-2 text-primary-500" />
            <Button variant="link">Email Support</Button>
          </div>
          <div className="flex items-center">
            <Phone className="mr-2 text-primary-500" />
            <Button variant="link">Phone Support: +1 (800) 123-4567</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Contact Form</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <Input placeholder="Name" />
            <Input type="email" placeholder="Email" />
            <Input placeholder="Subject" />
            <Textarea placeholder="Description" />
            <div className="flex items-center">
              <Upload className="mr-2 text-primary-500" />
              <Button variant="outline" type="button">Attach Files</Button>
            </div>
            <Button type="submit" className="w-full">Submit</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ContactSupport;