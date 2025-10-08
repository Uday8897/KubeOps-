import React from 'react';
import Header from './Header';

const Layout = ({ children }) => {
  return (
    <div className="bg-gray-900 min-h-screen text-gray-100 font-sans">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;