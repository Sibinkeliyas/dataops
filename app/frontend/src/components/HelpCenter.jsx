import React from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Search } from 'lucide-react';

const categories = [
  { name: "Getting Started", icon: "🚀" },
  { name: "Data Catalog", icon: "📊" },
  { name: "BI & Analytics", icon: "📈" },
  { name: "Machine Learning & AI", icon: "🤖" },
  { name: "AI Copilot", icon: "🤝" },
  { name: "AR Solutions", icon: "👓" },
  { name: "DataOps Portal", icon: "🔧" }
];

const popularArticles = [
  { title: "How to access the Data Catalog", views: 1205 },
  { title: "Creating your first Power BI report", views: 987 },
  { title: "Understanding AI Copilot features", views: 856 },
  { title: "Troubleshooting common DataOps issues", views: 743 },
  { title: "Best practices for data governance", views: 692 }
];

const HelpCenter = () => {
  return (
    <div className="space-y-6">
      <div className="relative">
        <Input
          type="text"
          placeholder="Search articles, FAQs, and guides..."
          className="pl-10 pr-4 py-2 w-full"
        />
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {categories.map((category, index) => (
                <li key={index} className="flex items-center">
                  <span className="mr-2">{category.icon}</span>
                  <Button variant="link">{category.name}</Button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Popular Articles</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {popularArticles.map((article, index) => (
                <li key={index} className="flex justify-between items-center">
                  <Button variant="link">{article.title}</Button>
                  <span className="text-sm text-gray-500">{article.views} views</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default HelpCenter;