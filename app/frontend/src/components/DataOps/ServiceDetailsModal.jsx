import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

const ServiceDetailsModal = ({ service }) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">Details</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{service.name} Details</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 items-center gap-4">
            <span className="font-bold">Status:</span>
            <span>{service.status}</span>
          </div>
          {Object.entries(service).slice(2).map(([key, value], index) => (
            <div key={index} className="grid grid-cols-2 items-center gap-4">
              <span className="font-bold">{key}:</span>
              <span>{value}</span>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ServiceDetailsModal;