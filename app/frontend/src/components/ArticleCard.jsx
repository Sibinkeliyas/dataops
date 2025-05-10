import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from 'react-router-dom';

const ArticleCard = ({ title, excerpt, link }) => {
  return (
    <Card className="bg-white bg-opacity-90">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-primary-600">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-700 mb-4">{excerpt}</p>
        <Link to={link} className="text-primary-500 hover:text-primary-600">Read more</Link>
      </CardContent>
    </Card>
  );
};

export default ArticleCard;