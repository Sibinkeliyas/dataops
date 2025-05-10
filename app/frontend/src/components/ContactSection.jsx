import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const ContactSection = () => {
  return (
    <section className="mb-12">
      <h3 className="text-2xl font-bold text-white mb-6">Connect with Us</h3>
      <Card className="bg-white bg-opacity-90">
        <CardHeader>
          <CardTitle>Get in Touch</CardTitle>
        </CardHeader>
        <CardContent>
          <p><strong>Email:</strong> mithril@dataplatform.allnex.com</p>
          <p><strong>Phone:</strong> +1 (800) 123-4567</p>
          <p><strong>Address:</strong> 123 Innovation Drive, Tech City, Country</p>
          <p className="mt-4">Empowering allnex teams to make data-driven decisions, protect valuable assets, and drive innovation forward.</p>
        </CardContent>
      </Card>
    </section>
  );
};

export default ContactSection;