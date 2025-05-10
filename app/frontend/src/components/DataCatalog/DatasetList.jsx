import React from 'react';
import DatasetCard from './DatasetCard';
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

const DatasetList = ({ datasets, isLoading, error, onSelectDataset }) => {
  if (isLoading) return <div>Loading datasets...</div>;
  if (error) return <div>Error loading datasets: {error.message}</div>;

  const filters = [
    { name: 'Data Domains', options: ['Finance', 'Sales', 'Supply Chain', 'Operations'] },
    { name: 'Classification', options: ['Public', 'Confidential', 'Restricted'] },
    { name: 'Source Systems', options: ['SAP', 'CRM', 'Legacy Systems'] },
  ];

  return (
    <div className="flex">
      <div className="w-1/4 pr-4">
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Filters</h2>
            {filters.map((filter) => (
              <div key={filter.name} className="mb-4">
                <h3 className="font-semibold mb-2">{filter.name}</h3>
                {filter.options.map((option) => (
                  <div key={option} className="flex items-center mb-2">
                    <Checkbox id={option} />
                    <Label htmlFor={option} className="ml-2">{option}</Label>
                  </div>
                ))}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      <div className="w-3/4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {datasets.map((dataset) => (
            <DatasetCard
              key={dataset.id}
              dataset={dataset}
              onSelect={() => onSelectDataset(dataset)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default DatasetList;