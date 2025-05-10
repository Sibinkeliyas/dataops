import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Calendar, Video, GraduationCap } from 'lucide-react';

const upcomingWebinars = [
  { title: "Introduction to Data Catalog", date: "2023-05-15", time: "14:00 UTC", speaker: "Jane Doe" },
  { title: "Advanced Power BI Techniques", date: "2023-05-20", time: "15:30 UTC", speaker: "John Smith" },
  { title: "AI Copilot Masterclass", date: "2023-05-25", time: "13:00 UTC", speaker: "Alice Johnson" },
];

const videoTutorials = [
  { title: "Getting Started with Mithril", duration: "15 min" },
  { title: "Data Catalog Deep Dive", duration: "25 min" },
  { title: "BI & Analytics Best Practices", duration: "20 min" },
  { title: "Intro to Machine Learning on Mithril", duration: "30 min" },
];

const certificationPrograms = [
  { title: "Mithril Data Platform Fundamentals", level: "Beginner" },
  { title: "Advanced Data Analytics with Mithril", level: "Intermediate" },
  { title: "AI and Machine Learning Certification", level: "Advanced" },
  { title: "DataOps Expert Certification", level: "Expert" },
];

const TrainingTutorials = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="mr-2 text-primary-500" /> Upcoming Webinars
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-4">
            {upcomingWebinars.map((webinar, index) => (
              <li key={index} className="flex justify-between items-center">
                <div>
                  <p className="font-semibold">{webinar.title}</p>
                  <p className="text-sm text-gray-500">{webinar.date} at {webinar.time} - Speaker: {webinar.speaker}</p>
                </div>
                <Button>Register</Button>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Video className="mr-2 text-primary-500" /> Video Tutorials
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {videoTutorials.map((tutorial, index) => (
              <li key={index} className="flex justify-between items-center">
                <Button variant="link">{tutorial.title}</Button>
                <span className="text-sm text-gray-500">{tutorial.duration}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <GraduationCap className="mr-2 text-primary-500" /> Certification Programs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {certificationPrograms.map((program, index) => (
              <li key={index} className="flex justify-between items-center">
                <Button variant="link">{program.title}</Button>
                <span className="text-sm text-gray-500">{program.level}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrainingTutorials;