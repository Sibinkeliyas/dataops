import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const ReportList = ({ reports, isLoading, error, onSelectReport }) => {
  if (isLoading) return <div>Loading reports...</div>;
  if (error) return <div>Error loading reports: {error.message}</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {reports.map((report) => (
        <Card key={report.id}>
          <CardHeader>
            <CardTitle>{report.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-4">{report.description}</p>
            <Button onClick={() => onSelectReport(report)}>View Details</Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default ReportList;