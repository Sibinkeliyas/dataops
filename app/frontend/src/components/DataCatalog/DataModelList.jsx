import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const DataModelList = ({ dataModels, isLoading, error, onSelectDataModel }) => {
  if (isLoading) return <div>Loading data models...</div>;
  if (error) return <div>Error loading data models: {error.message}</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {dataModels.map((model) => (
        <Card key={model.id}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{model.name}</span>
              <Badge>{model.source}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-2">{model.description}</p>
            <p className="text-xs text-gray-500 mb-4">Last updated: {model.lastUpdated}</p>
            <Button onClick={() => onSelectDataModel(model)}>View Details</Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DataModelList;