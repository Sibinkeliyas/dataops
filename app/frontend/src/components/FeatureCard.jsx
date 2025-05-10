import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from 'react-router-dom';

const FeatureCard = ({ icon, title, description, link }) => {
  return (
    <Card className="bg-white bg-opacity-90">
      <CardHeader>
        <CardTitle className="flex items-center">
          {icon}
          <span className="ml-2">{title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4">{description}</p>
        <Link to={link}>
          <Button variant="outline" className="w-full">Explore {title}</Button>
        </Link>
      </CardContent>
    </Card>
  );
};

export default FeatureCard;