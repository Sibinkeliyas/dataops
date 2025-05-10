import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchPlatformHealth, fetchRequestStats } from '../utils/dataFetching';

const Management = () => {
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['platformHealth'],
    queryFn: fetchPlatformHealth,
  });

  const { data: requestStats, isLoading: statsLoading } = useQuery({
    queryKey: ['requestStats'],
    queryFn: fetchRequestStats,
  });

  return (
    <div className="min-h-screen bg-primary-100">
      <header className="bg-primary-600 text-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold">Data Platform Management</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-white">
                <CardHeader>
                  <CardTitle className="text-primary-700">Platform Health</CardTitle>
                </CardHeader>
                <CardContent>
                  {healthLoading ? (
                    <p>Loading health data...</p>
                  ) : (
                    <ul>
                      {healthData.map((component) => (
                        <li key={component.name} className="flex justify-between items-center mb-2">
                          <span className="text-gray-700">{component.name}</span>
                          <span className={`px-2 py-1 rounded ${component.status === 'Healthy' ? 'bg-green-500' : 'bg-red-500'} text-white`}>
                            {component.status}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
              <Card className="bg-white">
                <CardHeader>
                  <CardTitle className="text-primary-700">Request Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  {statsLoading ? (
                    <p>Loading request statistics...</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={requestStats}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="incoming" fill="#0077BE" />
                        <Bar dataKey="outgoing" fill="#FFB81C" />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Management;