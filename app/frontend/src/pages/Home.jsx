import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Home = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <div className="relative w-full" style={{ paddingTop: '40%' }}> {/* Adjusted for ultra-wide */}
        <video
          className="absolute top-0 left-0 w-full h-full object-cover"
          autoPlay
          loop
          muted
          playsInline
        >
          <source src="/background-movie.mov" type="video/mov" />
          Your browser does not support the video tag.
        </video>
      </div>
      <div className="flex-grow p-6 md:p-8 lg:p-12">
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">Welcome back, User!</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl md:text-2xl">My Tickets</CardTitle>
            </CardHeader>
            <CardContent>
              <p>You have 3 open tickets.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-xl md:text-2xl">Pipeline Health</CardTitle>
            </CardHeader>
            <CardContent>
              <p>All pipelines are running smoothly.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-xl md:text-2xl">Recent Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <p>No new alerts in the last 24 hours.</p>
            </CardContent>
          </Card>
          {/* Add more cards here for ultra-wide screens */}
        </div>
      </div>
    </div>
  );
};

export default Home;