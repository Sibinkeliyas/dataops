import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export const NewsSection = () => {
  const news = [
    {
      title: "allnex Data Platform Reaches 1 Million Users",
      date: "2023-03-15",
      excerpt: "Our data platform has hit a major milestone with 1 million active users worldwide.",
    },
    {
      title: "New Feature: Advanced Predictive Analytics",
      date: "2023-04-02",
      excerpt: "We've launched a new suite of predictive analytics tools to help you forecast trends with greater accuracy.",
    },
    {
      title: "Upcoming Webinar: Mastering Data Visualization",
      date: "2023-04-20",
      excerpt: "Join our expert panel to learn advanced techniques for creating impactful data visualizations.",
    },
  ];

  return (
    <div className="mb-12">
      <h3 className="text-2xl font-bold text-primary-700 mb-4">Latest News</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {news.map((item, index) => (
          <Card key={index} className="bg-white">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-primary-600">{item.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 mb-2">{item.date}</p>
              <p className="text-gray-700">{item.excerpt}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};