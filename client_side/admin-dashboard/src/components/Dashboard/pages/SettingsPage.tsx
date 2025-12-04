import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Bell, Shield, Palette, Mail, Save } from 'lucide-react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    displayName: 'Admin User',
    email: 'admin@diamondaccounts.com',
    phone: '+91 98765 43210',
    notifications: {
      email: true,
      push: true,
      sms: false,
    },
    security: {
      twoFactor: false,
      sessionTimeout: '30',
    },
    preferences: {
      theme: 'light',
      language: 'en',
      dateFormat: 'DD/MM/YYYY',
    },
  });

  const handleSave = () => {
    // Simulate save
    alert('Settings saved successfully!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-600">Manage your account and application preferences</p>
      </div>

      {/* Profile Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card>
          <div className="flex items-center gap-3 mb-6">
            <User className="text-primary" size={24} />
            <h2 className="text-xl font-bold text-gray-800">Profile Information</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
              <input
                type="text"
                value={settings.displayName}
                onChange={(e) => setSettings({ ...settings, displayName: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input
                  type="email"
                  value={settings.email}
                  onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input
                  type="tel"
                  value={settings.phone}
                  onChange={(e) => setSettings({ ...settings, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Notification Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <div className="flex items-center gap-3 mb-6">
            <Bell className="text-primary" size={24} />
            <h2 className="text-xl font-bold text-gray-800">Notifications</h2>
          </div>
          
          <div className="space-y-4">
            <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3">
                <Mail className="text-gray-600" size={20} />
                <div>
                  <p className="font-medium text-gray-800">Email Notifications</p>
                  <p className="text-sm text-gray-600">Receive updates via email</p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.email}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, email: e.target.checked }
                })}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
            </label>

            <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3">
                <Bell className="text-gray-600" size={20} />
                <div>
                  <p className="font-medium text-gray-800">Push Notifications</p>
                  <p className="text-sm text-gray-600">Receive push notifications in browser</p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.push}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, push: e.target.checked }
                })}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
            </label>

            <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3">
                <Mail className="text-gray-600" size={20} />
                <div>
                  <p className="font-medium text-gray-800">SMS Notifications</p>
                  <p className="text-sm text-gray-600">Receive updates via SMS</p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.sms}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, sms: e.target.checked }
                })}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
            </label>
          </div>
        </Card>
      </motion.div>

      {/* Security Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <div className="flex items-center gap-3 mb-6">
            <Shield className="text-primary" size={24} />
            <h2 className="text-xl font-bold text-gray-800">Security</h2>
          </div>
          
          <div className="space-y-4">
            <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
              <div>
                <p className="font-medium text-gray-800">Two-Factor Authentication</p>
                <p className="text-sm text-gray-600">Add an extra layer of security</p>
              </div>
              <input
                type="checkbox"
                checked={settings.security.twoFactor}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, twoFactor: e.target.checked }
                })}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
              <select
                value={settings.security.sessionTimeout}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, sessionTimeout: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="15">15 minutes</option>
                <option value="30">30 minutes</option>
                <option value="60">1 hour</option>
                <option value="120">2 hours</option>
              </select>
            </div>

            <Button variant="outline" className="w-full">Change Password</Button>
          </div>
        </Card>
      </motion.div>

      {/* Preferences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <div className="flex items-center gap-3 mb-6">
            <Palette className="text-primary" size={24} />
            <h2 className="text-xl font-bold text-gray-800">Preferences</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
              <select
                value={settings.preferences.theme}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, theme: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
              <select
                value={settings.preferences.language}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, language: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="mr">Marathi</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date Format</label>
              <select
                value={settings.preferences.dateFormat}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, dateFormat: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
              </select>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex justify-end"
      >
        <Button onClick={handleSave} className="flex items-center gap-2">
          <Save size={20} />
          Save All Changes
        </Button>
      </motion.div>
    </div>
  );
};
