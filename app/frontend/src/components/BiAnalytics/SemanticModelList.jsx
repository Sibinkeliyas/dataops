import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const SemanticModelList = ({ models }) => {
  return (
    <div className="space-y-6">
      {models.map((model) => (
        <Card key={model.id}>
          <CardHeader>
            <CardTitle>{model.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-2">{model.description}</p>
            <p className="text-xs text-gray-500 mb-2">Associated Reports: {model.associatedReports.join(', ')}</p>
            <p className="text-xs text-gray-500 mb-4">Owner: {model.owner}</p>
            <div className="flex space-x-2">
              <Button onClick={() => console.log('View model details')}>View Model</Button>
              <Button variant="outline" onClick={() => console.log('Use in new report')}>Use in New Report</Button>
              <Button variant="outline" onClick={() => console.log('Download model')}>Download</Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default SemanticModelList;