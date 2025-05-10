import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Star, Share2 } from 'lucide-react';

const ReportGrid = ({ reports }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {reports.map((report) => (
        <Card key={report.id}>
          <CardHeader>
            <CardTitle>{report.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <img src={report.thumbnail} alt={report.name} className="w-full h-40 object-cover mb-4" />
            <p className="text-sm mb-2">{report.description}</p>
            <p className="text-xs text-gray-500 mb-4">Last modified: {report.lastModified}</p>
            <div className="flex justify-between">
              <Button onClick={() => window.open(report.powerBiUrl, '_blank')}>Open in Power BI</Button>
              <Button variant="outline" onClick={() => console.log('Add to favorites')}><Star size={16} /></Button>
              <Button variant="outline" onClick={() => console.log('Share report')}><Share2 size={16} /></Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default ReportGrid;