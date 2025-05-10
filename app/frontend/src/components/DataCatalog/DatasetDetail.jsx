import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Lock, Unlock, BarChart2, Brain, Database } from 'lucide-react';
import DataLineage from './DataLineage';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const DatasetDetail = ({ dataset, onBack }) => {
  const renderTypeSpecificContent = () => {
    switch (dataset.type) {
      case 'Dashboard':
        return (
          <div>
            <h3 className="font-semibold mb-2">Dashboard Details:</h3>
            <p>Power BI URL: <a href={dataset.powerBiUrl} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">{dataset.powerBiUrl}</a></p>
            <Button className="mt-4" onClick={() => window.open(dataset.powerBiUrl, '_blank')}>Open in Power BI</Button>
          </div>
        );
      case 'AI Model':
        return (
          <div>
            <h3 className="font-semibold mb-2">AI Model Details:</h3>
            <p>Accuracy: {dataset.accuracy}</p>
            <p>Algorithm: {dataset.algorithm}</p>
          </div>
        );
      case 'Semantic Model':
        return (
          <div>
            <h3 className="font-semibold mb-2">Semantic Model Details:</h3>
            <p>Associated Reports:</p>
            <ul className="list-disc list-inside">
              {dataset.associatedReports.map((report, index) => (
                <li key={index}>{report}</li>
              ))}
            </ul>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <Button onClick={onBack} variant="outline" className="mb-4">
        <ArrowLeft className="mr-2" /> Back to Dataset List
      </Button>
      <h2 className="text-2xl font-bold mb-4">{dataset.name}</h2>
      <Badge variant={dataset.accessLevel === 'granted' ? 'success' : 'secondary'} className="mb-4">
        {dataset.accessLevel === 'granted' ? <Unlock className="mr-2" /> : <Lock className="mr-2" />}
        {dataset.accessLevel === 'granted' ? 'Access Granted' : 'Request Access'}
      </Badge>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
          {dataset.lineage && <TabsTrigger value="lineage">Lineage</TabsTrigger>}
        </TabsList>

        <TabsContent value="overview">
          <div className="space-y-4">
            <p>{dataset.description}</p>
            <div>
              <h3 className="font-semibold">Key Attributes:</h3>
              <ul className="list-disc list-inside">
                <li>Type: {dataset.type}</li>
                <li>Owner: {dataset.owner}</li>
                <li>Last Updated: {dataset.lastUpdated}</li>
              </ul>
            </div>
            {renderTypeSpecificContent()}
          </div>
        </TabsContent>

        <TabsContent value="details">
          <div className="space-y-4">
            {dataset.fields && (
              <div>
                <h3 className="font-semibold">Fields and Data Types:</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Field Name</TableHead>
                      <TableHead>Data Type</TableHead>
                      <TableHead>Description</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dataset.fields.map((field, index) => (
                      <TableRow key={index}>
                        <TableCell>{field.name}</TableCell>
                        <TableCell>{field.type}</TableCell>
                        <TableCell>{field.description}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
            {dataset.qualityMetrics && (
              <div>
                <h3 className="font-semibold">Data Quality Metrics:</h3>
                <ul className="list-disc list-inside">
                  <li>Completeness: {dataset.qualityMetrics.completeness}%</li>
                  <li>Uniqueness: {dataset.qualityMetrics.uniqueness}%</li>
                  <li>Validity: {dataset.qualityMetrics.validity}%</li>
                </ul>
              </div>
            )}
            {dataset.tags && (
              <div>
                <h3 className="font-semibold">Tags and Classifications:</h3>
                <div className="flex flex-wrap gap-2">
                  {dataset.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">{tag}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        {dataset.lineage && (
          <TabsContent value="lineage">
            <DataLineage lineageData={dataset.lineage} />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default DatasetDetail;