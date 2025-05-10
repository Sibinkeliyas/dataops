import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', cpu: 65, memory: 45, network: 70 },
  { name: 'Feb', cpu: 59, memory: 50, network: 65 },
  { name: 'Mar', cpu: 80, memory: 55, network: 75 },
  { name: 'Apr', cpu: 81, memory: 60, network: 80 },
  { name: 'May', cpu: 56, memory: 65, network: 85 },
  { name: 'Jun', cpu: 55, memory: 70, network: 90 },
];

const PerformanceGraphs = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>System Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU Usage" />
              <Line type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory Usage" />
              <Line type="monotone" dataKey="network" stroke="#ffc658" name="Network Usage" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Key Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-lg font-semibold">Uptime</h3>
              <p className="text-2xl font-bold text-green-500">99.99%</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold">Response Time</h3>
              <p className="text-2xl font-bold text-blue-500">120ms</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold">Error Rate</h3>
              <p className="text-2xl font-bold text-red-500">0.01%</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold">Throughput</h3>
              <p className="text-2xl font-bold text-purple-500">1000 req/s</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceGraphs;