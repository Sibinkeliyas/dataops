import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart, PieChart, LineChart, Search, Star, Share2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import ReportGrid from '../components/BiAnalytics/ReportGrid';
import SemanticModelList from '../components/BiAnalytics/SemanticModelList';
import { useQuery } from '@tanstack/react-query';
import { fetchReports, fetchSemanticModels } from '../utils/dataFetching.jsx';

const BiAnalytics = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('reports');

  const { data: reports, isLoading: reportsLoading, error: reportsError } = useQuery({
    queryKey: ['reports'],
    queryFn: fetchReports,
  });

  const { data: semanticModels, isLoading: modelsLoading, error: modelsError } = useQuery({
    queryKey: ['semanticModels'],
    queryFn: fetchSemanticModels,
  });

  const handleSearch = (e) => {
    e.preventDefault();
    // Implement search logic here
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <nav className="text-sm mb-4" aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          <li className="flex items-center">
            <Link to="/" className="text-blue-500">Home</Link>
            <span className="mx-2">/</span>
          </li>
          <li className="flex items-center">
            BI & Analytics
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">Business Intelligence and Analytics</h1>

      <form onSubmit={handleSearch} className="mb-8 flex flex-col sm:flex-row gap-4">
        <Input
          type="text"
          placeholder="Search reports and dashboards..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-grow"
        />
        <Button type="submit" className="whitespace-nowrap"><Search className="mr-2" /> Search</Button>
      </form>

      <Tabs defaultValue="reports" className="mb-8">
        <TabsList className="flex flex-wrap justify-start gap-2 mb-4">
          <TabsTrigger value="reports" onClick={() => setActiveTab('reports')}>Reports & Dashboards</TabsTrigger>
          <TabsTrigger value="models" onClick={() => setActiveTab('models')}>Semantic Models</TabsTrigger>
        </TabsList>
        <div className="mt-4">
          <TabsContent value="reports">
            {reportsLoading ? (
              <p>Loading reports...</p>
            ) : reportsError ? (
              <p>Error loading reports: {reportsError.message}</p>
            ) : (
              <ReportGrid reports={reports} />
            )}
          </TabsContent>
          <TabsContent value="models">
            {modelsLoading ? (
              <p>Loading semantic models...</p>
            ) : modelsError ? (
              <p>Error loading semantic models: {modelsError.message}</p>
            ) : (
              <SemanticModelList models={semanticModels} />
            )}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default BiAnalytics;