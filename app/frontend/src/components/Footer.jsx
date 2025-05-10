import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <p>&copy; 2024 allnex. All rights reserved.</p>
          <div>
            <a href="#" className="text-gray-300 hover:text-white mr-4">Support</a>
            <a href="#" className="text-gray-300 hover:text-white mr-4">Terms of Service</a>
            <a href="#" className="text-gray-300 hover:text-white">Privacy Policy</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;