import React from 'react';
import { motion } from 'framer-motion';
import { Bell, Search, User, LogOut } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white shadow-md px-6 py-4 sticky top-0 z-40"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <img 
            src="/DIAMOND ACCOUNTS LOGO.png" 
            alt="Diamond Accounts" 
            className="h-12 w-auto"
          />
          <div className="hidden md:flex items-center flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search clients, requests..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button className="relative p-2 text-gray-600 hover:text-primary transition-colors hover:bg-gray-100 rounded-lg">
            <Bell size={24} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          
          <div className="flex items-center gap-3 pl-4 border-l border-gray-300">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-gray-800">Admin User</p>
              <p className="text-xs text-gray-600">admin@diamondaccounts.com</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-semibold cursor-pointer hover:bg-primary-dark transition-colors">
              <User size={20} />
            </div>
            <button className="p-2 text-gray-600 hover:text-red-500 transition-colors hover:bg-gray-100 rounded-lg">
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};
