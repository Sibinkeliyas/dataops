import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import DatasetList from '../components/DataCatalog/DatasetList';
import DatasetDetail from '../components/DataCatalog/DatasetDetail';
import { useQuery } from '@tanstack/react-query';
import { fetchDatasets } from '../utils/dataFetching.jsx';

const DataCatalog = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDataset, setSelectedDataset] = useState(null);

  const { data: datasets, isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: fetchDatasets,
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
            Data Catalog
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">Data Catalog</h1>

      <form onSubmit={handleSearch} className="mb-8 flex flex-col sm:flex-row gap-4">
        <Input
          type="text"
          placeholder="Search datasets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-grow"
        />
        <Button type="submit" className="whitespace-nowrap"><Search className="mr-2" /> Search</Button>
      </form>

      {selectedDataset ? (
        <DatasetDetail dataset={selectedDataset} onBack={() => setSelectedDataset(null)} />
      ) : (
        <DatasetList
          datasets={datasets}
          isLoading={isLoading}
          error={error}
          onSelectDataset={setSelectedDataset}
        />
      )}
    </div>
  );
};

export default DataCatalog;