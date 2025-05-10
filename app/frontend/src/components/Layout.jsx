import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

const Layout = ({ children, userEmail }) => {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);

  const toggleSidebar = () => {
    setSidebarExpanded(!sidebarExpanded);
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar isExpanded={sidebarExpanded} toggleSidebar={toggleSidebar} />
      <div className="flex flex-col flex-1">
        <Header userEmail={userEmail} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto z-0 relative">
          {children}
        </main>
        <Footer className="md:block landscape:hidden" />
      </div>
    </div>
  );
};

export default Layout;