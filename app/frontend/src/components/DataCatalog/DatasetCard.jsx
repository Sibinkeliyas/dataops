import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lock, Eye, BarChart2, Brain, Database } from 'lucide-react';

const DatasetCard = ({ dataset, onSelect }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'Dashboard':
        return <BarChart2 className="text-blue-500" size={16} />;
      case 'AI Model':
        return <Brain className="text-purple-500" size={16} />;
      case 'Semantic Model':
        return <Database className="text-green-500" size={16} />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center">
            {getIcon(dataset.type)}
            <span className="ml-2">{dataset.name}</span>
          </span>
          {dataset.accessLevel === 'restricted' && <Lock className="text-yellow-500" size={16} />}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-2">{dataset.description}</p>
        <p className="text-sm mb-2">Type: {dataset.type}</p>
        <p className="text-sm mb-2">Owner: {dataset.owner}</p>
        <p className="text-sm mb-2">Last Updated: {dataset.lastUpdated}</p>
        <Badge variant={dataset.accessLevel === 'granted' ? 'success' : 'secondary'}>
          {dataset.accessLevel === 'granted' ? 'Access Granted' : 'Request Access'}
        </Badge>
      </CardContent>
      <CardFooter>
        <Button onClick={onSelect} className="w-full"><Eye className="mr-2" /> View Details</Button>
      </CardFooter>
    </Card>
  );
};

export default DatasetCard;