# 🚀 React.js + Axios API Integration Guide

## 📋 Table of Contents
- [🏁 Quick Start](#quick-start)
- [⚙️ Axios Setup](#axios-setup)
- [🔐 Authentication Flow](#authentication-flow)
- [📊 Dashboard Integration](#dashboard-integration)
- [📤 File Upload Workflow](#file-upload-workflow)
- [👥 Employee Management](#employee-management)
- [📄 Report Generation](#report-generation)
- [🧾 Individual Employee Export](#individual-employee-export)
- [🔧 Error Handling](#error-handling)
- [🧩 Custom Hooks](#custom-hooks)
- [📱 Complete Components](#complete-components)

---

## 🏁 Quick Start

### Installation
```bash
npm install axios
# or
yarn add axios
```

### Base Configuration
```javascript
// src/config/api.js
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-domain.com/api' 
  : 'http://127.0.0.1:8000/api';
```

---

## ⚙️ Axios Setup

### Create Axios Instance
```javascript
// src/services/api.js
import axios from 'axios';
import { API_BASE_URL } from '../config/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

---

## 🔐 Authentication Flow

### Auth Service
```javascript
// src/services/authService.js
import apiClient from './api';

class AuthService {
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register/', {
        username: userData.username,
        email: userData.email,
        first_name: userData.firstName,
        last_name: userData.lastName,
        password: userData.password,
        password2: userData.confirmPassword
      });
      
      return { success: true, user: response.data.data.user };
    } catch (error) {
      return { 
        success: false, 
        errors: error.response?.data?.errors || { message: error.message } 
      };
    }
  }

  async login(username, password) {
    try {
      const response = await apiClient.post('/auth/login/', {
        username,
        password
      });
      
      if (response.data.success) {
        const { token, user } = response.data.data;
        localStorage.setItem('authToken', token);
        localStorage.setItem('user', JSON.stringify(user));
        return { success: true, user, token };
      }
      
      return { success: false, errors: response.data.errors };
    } catch (error) {
      return { 
        success: false, 
        errors: error.response?.data?.errors || { message: error.message } 
      };
    }
  }

  async logout() {
    try {
      await apiClient.post('/auth/logout/');
    } finally {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
  }

  async checkAuth() {
    try {
      const response = await apiClient.get('/auth/check/');
      return { authenticated: true, user: response.data.user };
    } catch (error) {
      this.logout();
      return { authenticated: false };
    }
  }

  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  getToken() {
    return localStorage.getItem('authToken');
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

export default new AuthService();
```

### Auth Context Provider
```javascript
// src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    setLoading(true);
    try {
      if (authService.isAuthenticated()) {
        const result = await authService.checkAuth();
        if (result.authenticated) {
          setUser(result.user);
          setIsAuthenticated(true);
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    const result = await authService.login(username, password);
    if (result.success) {
      setUser(result.user);
      setIsAuthenticated(true);
    }
    return result;
  };

  const register = async (userData) => {
    const result = await authService.register(userData);
    return result;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Login Component
```javascript
// src/components/auth/LoginForm.jsx
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    const result = await login(formData.username, formData.password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setErrors(result.errors);
    }
    
    setLoading(false);
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className={`w-full p-2 border rounded-md ${
              errors.username ? 'border-red-500' : 'border-gray-300'
            }`}
            required
          />
          {errors.username && (
            <p className="text-red-500 text-sm mt-1">{errors.username}</p>
          )}
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className={`w-full p-2 border rounded-md ${
              errors.password ? 'border-red-500' : 'border-gray-300'
            }`}
            required
          />
          {errors.password && (
            <p className="text-red-500 text-sm mt-1">{errors.password}</p>
          )}
        </div>

        {errors.non_field_errors && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 rounded">
            {errors.non_field_errors.map((error, index) => (
              <p key={index} className="text-red-700 text-sm">{error}</p>
            ))}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
```

---

## 📊 Dashboard Integration

### Dashboard Service
```javascript
// src/services/dashboardService.js
import apiClient from './api';

class DashboardService {
  async getStats() {
    try {
      const response = await apiClient.get('/dashboard/stats/');
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || error.message 
      };
    }
  }
}

export default new DashboardService();
```

### Dashboard Hook
```javascript
// src/hooks/useDashboard.js
import { useState, useEffect } from 'react';
import dashboardService from '../services/dashboardService';

export const useDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await dashboardService.getStats();
      
      if (result.success) {
        setStats(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return { stats, loading, error, refetch: fetchStats };
};
```

### Dashboard Component
```javascript
// src/components/dashboard/Dashboard.jsx
import React from 'react';
import { useDashboard } from '../../hooks/useDashboard';
import StatsCard from './StatsCard';
import RecentUploads from './RecentUploads';

const Dashboard = () => {
  const { stats, loading, error } = useDashboard();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Error loading dashboard: {error}
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Payroll Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Uploads"
          value={stats.uploads.total}
          subtitle={`${stats.uploads.completed} completed`}
          color="blue"
        />
        <StatsCard
          title="Total Employees"
          value={stats.employees.total.toLocaleString()}
          color="green"
        />
        <StatsCard
          title="Total Reports"
          value={stats.reports.total}
          color="purple"
        />
        <StatsCard
          title="Total Disbursement"
          value={`₹${stats.disbursement.total.toLocaleString()}`}
          color="orange"
        />
      </div>

      {/* Recent Uploads */}
      <RecentUploads uploads={stats.recent_uploads} />
    </div>
  );
};

export default Dashboard;
```

---

## 📤 File Upload Workflow

### Upload Service
```javascript
// src/services/uploadService.js
import apiClient from './api';

class UploadService {
  async validateFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await apiClient.post('/uploads/validate/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: error.message }
      };
    }
  }

  async uploadFile(file, onUploadProgress) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await apiClient.post('/uploads/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onUploadProgress ? (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onUploadProgress(percentCompleted);
        } : undefined,
      });
      
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: error.message }
      };
    }
  }

  async getUploads() {
    try {
      const response = await apiClient.get('/uploads/');
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getUploadDetails(uploadId) {
    try {
      const response = await apiClient.get(`/uploads/${uploadId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async deleteUpload(uploadId) {
    try {
      const response = await apiClient.delete(`/uploads/${uploadId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }
}

export default new UploadService();
```

### File Upload Hook
```javascript
// src/hooks/useFileUpload.js
import { useState } from 'react';
import uploadService from '../services/uploadService';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [validating, setValidating] = useState(false);

  const validateFile = (file) => {
    const errors = [];
    
    if (!file) {
      errors.push('Please select a file to upload.');
      return errors;
    }
    
    const validExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    
    if (!validExtensions.includes(fileExtension)) {
      errors.push('Invalid file format. Please upload an Excel file (.xlsx or .xls).');
    }
    
    if (file.size > 10 * 1024 * 1024) {
      errors.push('File size exceeds 10MB limit.');
    }
    
    return errors;
  };

  const validateFileOnServer = async (file) => {
    setValidating(true);
    try {
      const result = await uploadService.validateFile(file);
      return result;
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setValidating(false);
    }
  };

  const uploadFile = async (file) => {
    setUploading(true);
    setProgress(0);
    
    try {
      const result = await uploadService.uploadFile(file, (progressPercent) => {
        setProgress(progressPercent);
      });
      return result;
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return {
    uploading,
    progress,
    validating,
    validateFile,
    validateFileOnServer,
    uploadFile
  };
};
```

### File Upload Component
```javascript
// src/components/upload/FileUpload.jsx
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFileUpload } from '../../hooks/useFileUpload';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const {
    uploading,
    progress,
    validating,
    validateFile,
    validateFileOnServer,
    uploadFile
  } = useFileUpload();

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setErrors([]);
    setWarnings([]);
    
    // Client-side validation
    const validationErrors = validateFile(file);
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleValidate = async () => {
    if (!selectedFile) return;
    
    const result = await validateFileOnServer(selectedFile);
    
    if (result.success) {
      setErrors([]);
      setWarnings(result.data.warnings || []);
    } else {
      setErrors(result.error.errors || [result.error.message]);
      setWarnings([]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    const result = await uploadFile(selectedFile);
    
    if (result.success) {
      navigate(`/uploads/${result.data.data.id}`);
    } else {
      setErrors(result.error.errors || [result.error.message]);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Upload Payroll File</h2>
      
      {/* Drag & Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="space-y-4">
          <div className="text-4xl text-gray-400">📄</div>
          <div>
            <p className="text-lg font-medium">
              {selectedFile ? selectedFile.name : 'Choose or drag Excel file'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Supported formats: .xlsx, .xls (Max 10MB)
            </p>
          </div>
          <button
            type="button"
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
          >
            Browse Files
          </button>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileInputChange}
          className="hidden"
        />
      </div>

      {/* Progress Bar */}
      {(uploading || validating) && (
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span>{validating ? 'Validating...' : 'Uploading...'}</span>
            <span>{uploading ? `${progress}%` : ''}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ 
                width: uploading ? `${progress}%` : validating ? '100%' : '0%' 
              }}
            ></div>
          </div>
        </div>
      )}

      {/* Errors */}
      {errors.length > 0 && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 rounded">
          <h3 className="font-medium text-red-800">Validation Errors:</h3>
          <ul className="mt-2 text-sm text-red-700">
            {errors.map((error, index) => (
              <li key={index}>• {error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="mt-4 p-4 bg-yellow-100 border border-yellow-400 rounded">
          <h3 className="font-medium text-yellow-800">Warnings:</h3>
          <ul className="mt-2 text-sm text-yellow-700">
            {warnings.map((warning, index) => (
              <li key={index}>• {warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      {selectedFile && errors.length === 0 && (
        <div className="mt-6 flex space-x-4">
          <button
            onClick={handleValidate}
            disabled={validating}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            {validating ? 'Validating...' : 'Validate File'}
          </button>
          
          <button
            onClick={handleUpload}
            disabled={uploading || validating}
            className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
```

---

## 👥 Employee Management

### Employee Service
```javascript
// src/services/employeeService.js
import apiClient from './api';

class EmployeeService {
  async getEmployeesList(uploadId) {
    try {
      const response = await apiClient.get(`/uploads/${uploadId}/employees/`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getEmployeeDetails(employeeId) {
    try {
      const response = await apiClient.get(`/employees/${employeeId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async exportEmployee(employeeId, reportType) {
    try {
      const response = await apiClient.post(
        `/employees/${employeeId}/export/`,
        { report_type: reportType },
        { responseType: 'blob' }
      );

      const blob = new Blob([response.data]);
      const filename = this.extractFilename(response.headers['content-disposition']) ||
        `employee_${employeeId}_payroll.${reportType === 'excel' ? 'xlsx' : 'pdf'}`;

      return { success: true, blob, filename };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  extractFilename(contentDisposition) {
    if (!contentDisposition) return null;
    const match = contentDisposition.match(/filename="(.+)"/);
    return match ? match[1] : null;
  }

  downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

export default new EmployeeService();
```

### Employee Hook
```javascript
// src/hooks/useEmployees.js
import { useState, useEffect } from 'react';
import employeeService from '../services/employeeService';

export const useEmployees = (uploadId) => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEmployees = async () => {
    if (!uploadId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await employeeService.getEmployeesList(uploadId);
      
      if (result.success) {
        setEmployees(result.data.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [uploadId]);

  const exportEmployee = async (employeeId, reportType) => {
    try {
      const result = await employeeService.exportEmployee(employeeId, reportType);
      
      if (result.success) {
        employeeService.downloadBlob(result.blob, result.filename);
        return { success: true };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  return {
    employees,
    loading,
    error,
    refetch: fetchEmployees,
    exportEmployee
  };
};
```

### Employee List Component
```javascript
// src/components/employees/EmployeeList.jsx
import React, { useState } from 'react';
import { useEmployees } from '../../hooks/useEmployees';
import EmployeeCard from './EmployeeCard';
import EmployeeModal from './EmployeeModal';

const EmployeeList = ({ uploadId }) => {
  const { employees, loading, error, exportEmployee } = useEmployees(uploadId);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [exportLoading, setExportLoading] = useState({});

  const handleViewEmployee = (employee) => {
    setSelectedEmployee(employee);
    setShowModal(true);
  };

  const handleExport = async (employeeId, reportType) => {
    setExportLoading(prev => ({ ...prev, [`${employeeId}_${reportType}`]: true }));
    
    try {
      const result = await exportEmployee(employeeId, reportType);
      
      if (!result.success) {
        alert(`Export failed: ${result.error}`);
      }
    } finally {
      setExportLoading(prev => ({ ...prev, [`${employeeId}_${reportType}`]: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Error loading employees: {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Employees ({employees.length})</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {employees.map((employee) => (
          <EmployeeCard
            key={employee.id}
            employee={employee}
            onView={() => handleViewEmployee(employee)}
            onExport={handleExport}
            exportLoading={exportLoading}
          />
        ))}
      </div>

      {/* Employee Details Modal */}
      {showModal && selectedEmployee && (
        <EmployeeModal
          employee={selectedEmployee}
          isOpen={showModal}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default EmployeeList;
```

### Employee Card Component
```javascript
// src/components/employees/EmployeeCard.jsx
import React from 'react';

const EmployeeCard = ({ employee, onView, onExport, exportLoading }) => {
  const { salary } = employee;
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold">{employee.name}</h3>
          <p className="text-sm text-gray-600">ID: {employee.employee_id}</p>
        </div>
        <button
          onClick={onView}
          className="text-blue-500 hover:text-blue-700 text-sm"
        >
          View Details
        </button>
      </div>

      <div className="space-y-2 mb-4">
        <p className="text-sm">
          <span className="font-medium">Department:</span> {employee.department || 'N/A'}
        </p>
        <p className="text-sm">
          <span className="font-medium">Designation:</span> {employee.designation || 'N/A'}
        </p>
        <p className="text-sm">
          <span className="font-medium">Net Salary:</span>
          <span className="text-green-600 font-semibold ml-1">
            ₹{parseFloat(salary.net_salary).toLocaleString()}
          </span>
        </p>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => onExport(employee.id, 'excel')}
          disabled={exportLoading[`${employee.id}_excel`]}
          className="flex-1 bg-green-500 text-white py-2 px-3 rounded-md text-sm hover:bg-green-600 disabled:opacity-50"
        >
          {exportLoading[`${employee.id}_excel`] ? '...' : '📊 Excel'}
        </button>
        
        <button
          onClick={() => onExport(employee.id, 'pdf')}
          disabled={exportLoading[`${employee.id}_pdf`]}
          className="flex-1 bg-red-500 text-white py-2 px-3 rounded-md text-sm hover:bg-red-600 disabled:opacity-50"
        >
          {exportLoading[`${employee.id}_pdf`] ? '...' : '📄 PDF'}
        </button>
      </div>
    </div>
  );
};

export default EmployeeCard;
```

---

## 📄 Report Generation

### Report Service
```javascript
// src/services/reportService.js
import apiClient from './api';

class ReportService {
  async generateReport(uploadId, reportType) {
    try {
      const response = await apiClient.post(
        `/uploads/${uploadId}/reports/generate/`,
        { report_type: reportType }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getAllReports() {
    try {
      const response = await apiClient.get('/reports/');
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getReportDetails(reportId) {
    try {
      const response = await apiClient.get(`/reports/${reportId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  downloadReport(fileUrl) {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileUrl.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

export default new ReportService();
```

### Report Hook
```javascript
// src/hooks/useReports.js
import { useState, useEffect } from 'react';
import reportService from '../services/reportService';

export const useReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await reportService.getAllReports();
      
      if (result.success) {
        setReports(result.data.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (uploadId, reportType) => {
    try {
      const result = await reportService.generateReport(uploadId, reportType);
      
      if (result.success) {
        await fetchReports(); // Refresh the list
        return { success: true, report: result.data.data };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return {
    reports,
    loading,
    error,
    generateReport,
    refetch: fetchReports,
    downloadReport: reportService.downloadReport
  };
};
```

### Report Generation Component
```javascript
// src/components/reports/ReportGenerator.jsx
import React, { useState } from 'react';
import { useReports } from '../../hooks/useReports';

const ReportGenerator = ({ uploadId, uploadName }) => {
  const [generating, setGenerating] = useState({ excel: false, pdf: false });
  const { generateReport } = useReports();

  const handleGenerateReport = async (reportType) => {
    setGenerating(prev => ({ ...prev, [reportType]: true }));
    
    try {
      const result = await generateReport(uploadId, reportType);
      
      if (result.success) {
        alert(`${reportType.toUpperCase()} report generated successfully!`);
      } else {
        alert(`Report generation failed: ${result.error}`);
      }
    } finally {
      setGenerating(prev => ({ ...prev, [reportType]: false }));
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-4">Generate Reports</h3>
      <p className="text-gray-600 mb-4">Upload: {uploadName}</p>
      
      <div className="flex space-x-4">
        <button
          onClick={() => handleGenerateReport('excel')}
          disabled={generating.excel}
          className="flex items-center px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
        >
          {generating.excel ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <span className="mr-2">📊</span>
          )}
          {generating.excel ? 'Generating...' : 'Generate Excel'}
        </button>
        
        <button
          onClick={() => handleGenerateReport('pdf')}
          disabled={generating.pdf}
          className="flex items-center px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50"
        >
          {generating.pdf ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <span className="mr-2">📄</span>
          )}
          {generating.pdf ? 'Generating...' : 'Generate PDF'}
        </button>
      </div>
    </div>
  );
};

export default ReportGenerator;
```

### Reports List Component
```javascript
// src/components/reports/ReportsList.jsx
import React from 'react';
import { useReports } from '../../hooks/useReports';
import { formatDate } from '../../utils/dateUtils';

const ReportsList = () => {
  const { reports, loading, error, downloadReport } = useReports();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Error loading reports: {error}
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No reports generated yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Generated Reports</h2>
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Upload File
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Generated Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Size
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {reports.map((report) => (
              <tr key={report.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {report.upload.filename}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    report.report_type === 'excel' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {report.report_type.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(report.generated_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {report.file_size_kb} KB
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => downloadReport(report.file)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Download
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportsList;
```

---

## 🧾 Individual Employee Export

Already covered in the Employee Management section above. The `useEmployees` hook and `EmployeeCard` component handle individual employee exports.

---

## 🔧 Error Handling

### Error Boundary Component
```javascript
// src/components/common/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <h2 className="text-lg font-semibold mb-2">Something went wrong</h2>
            <p>{this.state.error?.message || 'An unexpected error occurred'}</p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### Global Error Handler
```javascript
// src/utils/errorHandler.js
export const handleApiError = (error, showNotification) => {
  console.error('API Error:', error);

  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 401:
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      
      case 403:
        showNotification('error', 'You do not have permission to perform this action.');
        return;
      
      case 404:
        showNotification('error', 'The requested resource was not found.');
        return;
      
      case 422:
        // Validation errors
        if (data.errors) {
          const errorMessages = Object.values(data.errors).flat();
          showNotification('error', errorMessages.join(', '));
        } else {
          showNotification('error', data.message || 'Validation failed.');
        }
        return;
      
      case 500:
        showNotification('error', 'Server error occurred. Please try again later.');
        return;
      
      default:
        showNotification('error', data.message || `HTTP ${status} error occurred.`);
        return;
    }
  } else if (error.request) {
    showNotification('error', 'Network error. Please check your connection.');
  } else {
    showNotification('error', error.message || 'An unexpected error occurred.');
  }
};

// Form validation utilities
export const validateUploadFile = (file) => {
  const errors = [];
  
  if (!file) {
    errors.push('Please select a file to upload.');
    return errors;
  }
  
  const validExtensions = ['.xlsx', '.xls'];
  const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
  
  if (!validExtensions.includes(fileExtension)) {
    errors.push('Invalid file format. Please upload an Excel file (.xlsx or .xls).');
  }
  
  if (file.size > 10 * 1024 * 1024) {
    errors.push('File size exceeds 10MB limit.');
  }
  
  return errors;
};
```

---

## 🧩 Custom Hooks

### useNotification Hook
```javascript
// src/hooks/useNotification.js
import { useState } from 'react';

export const useNotification = () => {
  const [notifications, setNotifications] = useState([]);

  const showNotification = (type, message, duration = 5000) => {
    const id = Date.now();
    const notification = { id, type, message };
    
    setNotifications(prev => [...prev, notification]);
    
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return {
    notifications,
    showNotification,
    removeNotification,
    showSuccess: (message, duration) => showNotification('success', message, duration),
    showError: (message, duration) => showNotification('error', message, duration),
    showWarning: (message, duration) => showNotification('warning', message, duration),
    showInfo: (message, duration) => showNotification('info', message, duration),
  };
};
```

### useApi Hook
```javascript
// src/hooks/useApi.js
import { useState, useCallback } from 'react';
import { handleApiError } from '../utils/errorHandler';
import { useNotification } from './useNotification';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const { showNotification } = useNotification();

  const execute = useCallback(async (apiCall) => {
    setLoading(true);
    try {
      const result = await apiCall();
      return result;
    } catch (error) {
      handleApiError(error, showNotification);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  return { loading, execute };
};
```

### usePagination Hook
```javascript
// src/hooks/usePagination.js
import { useState, useMemo } from 'react';

export const usePagination = (data, itemsPerPage = 10) => {
  const [currentPage, setCurrentPage] = useState(1);

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return data.slice(startIndex, startIndex + itemsPerPage);
  }, [data, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(data.length / itemsPerPage);

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToNextPage = () => goToPage(currentPage + 1);
  const goToPrevPage = () => goToPage(currentPage - 1);

  return {
    currentPage,
    totalPages,
    paginatedData,
    goToPage,
    goToNextPage,
    goToPrevPage,
    hasNextPage: currentPage < totalPages,
    hasPrevPage: currentPage > 1,
  };
};
```

---

## 📱 Complete Components

### Main App Component
```javascript
// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Navigation from './components/common/Navigation';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import Dashboard from './components/dashboard/Dashboard';
import FileUpload from './components/upload/FileUpload';
import UploadDetails from './components/upload/UploadDetails';
import EmployeeList from './components/employees/EmployeeList';
import ReportsList from './components/reports/ReportsList';
import NotificationContainer from './components/common/NotificationContainer';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Navigation />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/login" element={<LoginForm />} />
                <Route path="/register" element={<RegisterForm />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/upload"
                  element={
                    <ProtectedRoute>
                      <FileUpload />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/uploads/:id"
                  element={
                    <ProtectedRoute>
                      <UploadDetails />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/reports"
                  element={
                    <ProtectedRoute>
                      <ReportsList />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
            <NotificationContainer />
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
```

### Protected Route Component
```javascript
// src/components/auth/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### Utility Functions
```javascript
// src/utils/dateUtils.js
export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// src/utils/formatters.js
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatFileSize = (bytes) => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Byte';
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};
```

### Package.json Dependencies
```json
{
  "name": "payroll-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.1",
    "axios": "^1.3.4",
    "@tailwindcss/forms": "^0.5.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0",
    "tailwindcss": "^3.2.7",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.21"
  }
}
```

---

## 🔄 Complete Workflow Summary

### 1. User Journey Flow

```text
Registration → Login → Dashboard → Upload File → View Employees → Generate Reports → Export Individual Records
```

### 2. API Integration with Axios

```javascript
// Complete API integration example
import { useAuth } from './contexts/AuthContext';
import { useApi } from './hooks/useApi';
import uploadService from './services/uploadService';

const MyComponent = () => {
  const { user } = useAuth();
  const { loading, execute } = useApi();

  const handleUpload = async (file) => {
    await execute(async () => {
      const result = await uploadService.uploadFile(file);
      if (result.success) {
        // Handle success
        navigate(`/uploads/${result.data.data.id}`);
      }
    });
  };

  return (
    // Component JSX
  );
};
```

### 3. Error Handling Strategy

- Axios interceptors handle global authentication errors
- Error boundaries catch React component errors
- Custom useNotification hook provides user feedback
- Form validation with real-time error display
- Network error handling with retry mechanisms

### 4. File Download Pattern

- Use axios responseType: 'blob' for file downloads
- Extract filename from Content-Disposition header
- Create temporary download links with URL.createObjectURL
- Clean up object URLs after download

This React.js + Axios guide provides a complete, production-ready integration pattern for the Payroll Processor API! 🚀
