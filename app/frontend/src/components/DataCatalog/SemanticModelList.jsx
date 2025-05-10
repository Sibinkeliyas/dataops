import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const SemanticModelList = ({ semanticModels, isLoading, error, onSelectSemanticModel }) => {
  if (isLoading) return <div>Loading semantic models...</div>;
  if (error) return <div>Error loading semantic models: {error.message}</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {semanticModels.map((model) => (
        <Card key={model.id}>
          <CardHeader>
            <CardTitle>{model.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-2">{model.description}</p>
            <p className="text-xs text-gray-500 mb-4">Owner: {model.owner}</p>
            <Button onClick={() => onSelectSemanticModel(model)}>View Details</Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default SemanticModelList;