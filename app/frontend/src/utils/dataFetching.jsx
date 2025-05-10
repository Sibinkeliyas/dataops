// Simulated data fetching functions
export const fetchPlatformHealth = async () => {
  // In a real application, this would be an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { name: 'Database', status: 'Healthy' },
        { name: 'API Server', status: 'Healthy' },
        { name: 'Data Processing', status: 'Healthy' },
        { name: 'Storage', status: 'Warning' },
        { name: 'Authentication Service', status: 'Healthy' },
        { name: 'Caching Layer', status: 'Healthy' },
        { name: 'Load Balancer', status: 'Healthy' },
        { name: 'Message Queue', status: 'Warning' },
        { name: 'Logging Service', status: 'Healthy' },
        { name: 'Backup System', status: 'Healthy' },
      ]);
    }, 1000);
  });
};

export const fetchRequestStats = async () => {
  // In a real application, this would be an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { name: 'Team A', incoming: 400, outgoing: 240, processed: 380 },
        { name: 'Team B', incoming: 300, outgoing: 139, processed: 280 },
        { name: 'Team C', incoming: 200, outgoing: 980, processed: 190 },
        { name: 'Team D', incoming: 278, outgoing: 390, processed: 250 },
        { name: 'Team E', incoming: 189, outgoing: 480, processed: 170 },
        { name: 'Team F', incoming: 239, outgoing: 380, processed: 220 },
        { name: 'Team G', incoming: 349, outgoing: 430, processed: 310 },
        { name: 'Team H', incoming: 178, outgoing: 290, processed: 160 },
        { name: 'Team I', incoming: 289, outgoing: 350, processed: 270 },
        { name: 'Team J', incoming: 329, outgoing: 420, processed: 300 },
      ]);
    }, 1000);
  });
};

export const fetchInfrastructureData = async () => {
  // In a real application, this would be an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        services: [
          { 
            name: 'Azure Data Lake', 
            status: 'Operational', 
            storageUsed: '70%',
            dataTransferred: '1.2 TB/day',
            activeConnections: 150,
            readOperations: '500K/hour',
            writeOperations: '200K/hour'
          },
          { 
            name: 'Databricks Clusters', 
            status: 'Warning', 
            activeNodes: 25,
            jobsRunning: 10,
            clusterUtilization: '80%',
            sparkApplications: 15,
            averageExecutionTime: '45 minutes'
          },
          { 
            name: 'Azure Synapse', 
            status: 'Operational', 
            activeQueries: 50,
            dataProcessed: '500 GB/hour',
            cacheHitRatio: '85%',
            concurrentUsers: 30,
            averageQueryDuration: '2.5 seconds'
          },
          { 
            name: 'Power BI Service', 
            status: 'Operational', 
            activeUsers: 500,
            reportsViewed: 1000,
            averageLoadTime: '2.5s',
            dataRefreshes: 50,
            datasetSize: '250 GB'
          },
          { 
            name: 'Azure Data Factory', 
            status: 'Issue', 
            pipelinesRunning: 15,
            dataFlowExecutions: 100,
            integrationRuntimeUtilization: '90%',
            successRate: '95%',
            averagePipelineDuration: '30 minutes'
          },
        ],
        utilizationHistory: [
          { timestamp: '08:00', cpuUsage: 30, memoryUsage: 40, storageUsage: 50, networkUsage: 25 },
          { timestamp: '09:00', cpuUsage: 35, memoryUsage: 45, storageUsage: 52, networkUsage: 30 },
          { timestamp: '10:00', cpuUsage: 50, memoryUsage: 60, storageUsage: 55, networkUsage: 40 },
          { timestamp: '11:00', cpuUsage: 65, memoryUsage: 70, storageUsage: 58, networkUsage: 55 },
          { timestamp: '12:00', cpuUsage: 70, memoryUsage: 75, storageUsage: 60, networkUsage: 60 },
          { timestamp: '13:00', cpuUsage: 68, memoryUsage: 73, storageUsage: 62, networkUsage: 58 },
          { timestamp: '14:00', cpuUsage: 60, memoryUsage: 70, storageUsage: 65, networkUsage: 50 },
          { timestamp: '15:00', cpuUsage: 55, memoryUsage: 65, storageUsage: 67, networkUsage: 45 },
          { timestamp: '16:00', cpuUsage: 40, memoryUsage: 50, storageUsage: 70, networkUsage: 35 },
          { timestamp: '17:00', cpuUsage: 30, memoryUsage: 45, storageUsage: 72, networkUsage: 25 },
        ],
      });
    }, 1000);
  });
};

export const fetchUsageData = async () => {
  // In a real application, this would be an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        metrics: [
          { name: 'Monday', activeUsers: 120, reportsViewed: 450, queriesRun: 1200, dataProcessed: 500 },
          { name: 'Tuesday', activeUsers: 150, reportsViewed: 500, queriesRun: 1500, dataProcessed: 600 },
          { name: 'Wednesday', activeUsers: 180, reportsViewed: 550, queriesRun: 1800, dataProcessed: 700 },
          { name: 'Thursday', activeUsers: 200, reportsViewed: 600, queriesRun: 2000, dataProcessed: 750 },
          { name: 'Friday', activeUsers: 170, reportsViewed: 520, queriesRun: 1700, dataProcessed: 650 },
          { name: 'Saturday', activeUsers: 90, reportsViewed: 300, queriesRun: 800, dataProcessed: 300 },
          { name: 'Sunday', activeUsers: 80, reportsViewed: 250, queriesRun: 600, dataProcessed: 250 },
        ],
        topReports: [
          { name: 'Sales Dashboard', views: 1200, uniqueUsers: 150, avgLoadTime: 2.5, dataSize: '50 MB' },
          { name: 'Inventory Analysis', views: 950, uniqueUsers: 120, avgLoadTime: 3.1, dataSize: '75 MB' },
          { name: 'Customer Insights', views: 800, uniqueUsers: 100, avgLoadTime: 2.8, dataSize: '60 MB' },
          { name: 'Financial Summary', views: 750, uniqueUsers: 80, avgLoadTime: 3.5, dataSize: '100 MB' },
          { name: 'Product Performance', views: 700, uniqueUsers: 90, avgLoadTime: 2.9, dataSize: '55 MB' },
          { name: 'Marketing Campaign Analysis', views: 650, uniqueUsers: 70, avgLoadTime: 3.2, dataSize: '80 MB' },
          { name: 'Supply Chain Overview', views: 600, uniqueUsers: 60, avgLoadTime: 3.0, dataSize: '70 MB' },
          { name: 'HR Analytics', views: 550, uniqueUsers: 50, avgLoadTime: 2.7, dataSize: '45 MB' },
          { name: 'Quality Control Metrics', views: 500, uniqueUsers: 40, avgLoadTime: 2.6, dataSize: '40 MB' },
          { name: 'Customer Support KPIs', views: 450, uniqueUsers: 30, avgLoadTime: 2.4, dataSize: '35 MB' },
        ],
      });
    }, 1000);
  });
};

export const fetchAzureCostData = async () => {
  // In a real application, this would be an API call to Azure Cost Management
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        monthlyCosts: [
          { month: 'Jan', cost: 5000 },
          { month: 'Feb', cost: 5500 },
          { month: 'Mar', cost: 6000 },
          { month: 'Apr', cost: 5800 },
          { month: 'May', cost: 6200 },
          { month: 'Jun', cost: 6500 },
          { month: 'Jul', cost: 6800 },
          { month: 'Aug', cost: 7000 },
          { month: 'Sep', cost: 6900 },
          { month: 'Oct', cost: 6700 },
          { month: 'Nov', cost: 6600 },
          { month: 'Dec', cost: 6400 },
        ],
        serviceBreakdown: [
          { service: 'Azure Data Lake', cost: 2000 },
          { service: 'Azure Synapse', cost: 1500 },
          { service: 'Power BI', cost: 1000 },
          { service: 'Azure Data Factory', cost: 1200 },
          { service: 'Databricks', cost: 1800 },
          { service: 'Azure Functions', cost: 500 },
          { service: 'Azure Kubernetes Service', cost: 1000 },
          { service: 'Azure Monitor', cost: 300 },
          { service: 'Azure Storage', cost: 700 },
          { service: 'Other Services', cost: 500 },
        ],
        totalCost: 10500,
        budgetLimit: 12000,
        costTrend: '+5% from last month',
        savingsOpportunities: [
          { description: 'Right-size underutilized VMs', potentialSavings: 500 },
          { description: 'Use Azure Reservations', potentialSavings: 800 },
          { description: 'Optimize data transfer', potentialSavings: 300 },
        ],
      });
    }, 1000);
  });
};

export const fetchAlerts = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 1, type: 'Pipeline Failure', severity: 'High', timestamp: '2023-03-15 10:30 AM', message: 'Data ingestion pipeline failed due to network timeout', affectedSystem: 'ETL Pipeline' },
        { id: 2, type: 'Security Alert', severity: 'Medium', timestamp: '2023-03-16 02:15 PM', message: 'Unusual login activity detected from IP 192.168.1.100', affectedSystem: 'Authentication Service' },
        { id: 3, type: 'Ticket Update', severity: 'Low', timestamp: '2023-03-17 09:45 AM', message: 'Ticket #1234 has been resolved and closed', affectedSystem: 'Ticketing System' },
        { id: 4, type: 'System Performance', severity: 'Medium', timestamp: '2023-03-18 11:20 AM', message: 'High CPU usage detected on Web Server 2', affectedSystem: 'Web Server Cluster' },
        { id: 5, type: 'Database Alert', severity: 'High', timestamp: '2023-03-19 03:30 PM', message: 'Database replication lag exceeds 30 minutes', affectedSystem: 'Database Cluster' },
        { id: 6, type: 'Storage Warning', severity: 'Medium', timestamp: '2023-03-20 08:00 AM', message: 'Storage capacity reaching 85% on Data Lake', affectedSystem: 'Azure Data Lake' },
        { id: 7, type: 'API Performance', severity: 'Low', timestamp: '2023-03-21 01:45 PM', message: 'Increased latency in API responses', affectedSystem: 'API Gateway' },
        { id: 8, type: 'Compliance Alert', severity: 'High', timestamp: '2023-03-22 11:00 AM', message: 'Potential data breach detected, initiating lockdown', affectedSystem: 'Security Module' },
        { id: 9, type: 'Cost Alert', severity: 'Medium', timestamp: '2023-03-23 09:30 AM', message: 'Monthly Azure spending exceeded budget by 10%', affectedSystem: 'Azure Cost Management' },
        { id: 10, type: 'Data Quality', severity: 'Low', timestamp: '2023-03-24 04:00 PM', message: 'Data quality check failed for Customer dataset', affectedSystem: 'Data Quality Service' },
      ]);
    }, 1000);
  });
};

export const fetchPipelines = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 1, name: 'Customer Data Ingestion', status: 'Operational', lastRun: '2023-03-15 10:30 AM', successRate: '98%', avgDuration: '45 minutes' },
        { id: 2, name: 'Sales Data Transformation', status: 'Warning', lastRun: '2023-03-16 02:15 PM', successRate: '92%', avgDuration: '1 hour 15 minutes' },
        { id: 3, name: 'Product Inventory Sync', status: 'Operational', lastRun: '2023-03-17 09:45 AM', successRate: '99%', avgDuration: '30 minutes' },
        { id: 4, name: 'Financial Data Export', status: 'Issue', lastRun: '2023-03-18 11:20 AM', successRate: '85%', avgDuration: '2 hours' },
        { id: 5, name: 'Marketing Campaign Analytics', status: 'Operational', lastRun: '2023-03-19 03:30 PM', successRate: '97%', avgDuration: '1 hour' },
        { id: 6, name: 'User Behavior Tracking', status: 'Operational', lastRun: '2023-03-20 08:00 AM', successRate: '96%', avgDuration: '55 minutes' },
        { id: 7, name: 'Supply Chain Optimization', status: 'Warning', lastRun: '2023-03-21 01:45 PM', successRate: '91%', avgDuration: '1 hour 30 minutes' },
        { id: 8, name: 'Customer Sentiment Analysis', status: 'Operational', lastRun: '2023-03-22 11:00 AM', successRate: '98%', avgDuration: '40 minutes' },
        { id: 9, name: 'Fraud Detection System', status: 'Operational', lastRun: '2023-03-23 09:30 AM', successRate: '99.5%', avgDuration: '2 hours 30 minutes' },
        { id: 10, name: 'IoT Data Processing', status: 'Issue', lastRun: '2023-03-24 04:00 PM', successRate: '88%', avgDuration: '3 hours' },
      ]);
    }, 1000);
  });
};

export const fetchDashboardData = async () => {
  // In a real application, this would be an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        infrastructureStatus: 'Healthy',
        uptime: '99.99%',
        activeInfraAlerts: 2,
        pipelineStatus: 'Warning',
        pipelineSuccessRate: '98.5%',
        failedJobs: 3,
        dataQualityStatus: 'Healthy',
        dataQualityScore: '95/100',
        dataQualityIssues: 5,
        costStatus: 'Warning',
        monthlySpend: 15000,
        budgetUtilization: 85,
        securityStatus: 'Healthy',
        openVulnerabilities: 1,
        complianceScore: 98,
        ticketStatus: 'Healthy',
        openTickets: 12,
        avgResolutionTime: '4h 30m'
      });
    }, 1000);
  });
};

export const fetchTickets = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 1, title: 'Data pipeline failure', priority: 'High', status: 'Open', assignedTo: 'John Doe', createdDate: '2023-03-15', lastUpdated: '2023-03-16', source: 'JIRA', resolutionTime: 4, description: 'The main ETL pipeline is failing to process data from the sales database.', activityLog: ['Ticket created by John Doe on 2023-03-15', 'Assigned to Data Engineering team on 2023-03-15', 'Investigation started on 2023-03-16'] },
        { id: 2, title: 'Dashboard loading slowly', priority: 'Medium', status: 'In Progress', assignedTo: 'Jane Smith', createdDate: '2023-03-16', lastUpdated: '2023-03-17', source: 'ServiceNow', resolutionTime: 8, description: 'Users are reporting slow load times for the main sales dashboard.', activityLog: ['Ticket created by Jane Smith on 2023-03-16', 'Assigned to BI team on 2023-03-16', 'Initial analysis completed on 2023-03-17'] },
        { id: 3, title: 'Data quality issue in customer dataset', priority: 'High', status: 'Open', assignedTo: 'Bob Johnson', createdDate: '2023-03-17', lastUpdated: '2023-03-17', source: 'Azure DevOps', resolutionTime: 2, description: 'Multiple duplicate entries found in the customer dataset, affecting reporting accuracy.', activityLog: ['Ticket created by Bob Johnson on 2023-03-17', 'Escalated to Data Governance team on 2023-03-17'] },
        { id: 4, title: 'New data source integration request', priority: 'Low', status: 'Open', assignedTo: 'Alice Brown', createdDate: '2023-03-18', lastUpdated: '2023-03-18', source: 'JIRA', resolutionTime: 12, description: 'Request to integrate new social media analytics data source into our data lake.', activityLog: ['Ticket created by Alice Brown on 2023-03-18', 'Pending review by Data Architecture team'] },
        { id: 5, title: 'Automated report delivery failure', priority: 'Medium', status: 'Closed', assignedTo: 'Charlie Davis', createdDate: '2023-03-14', lastUpdated: '2023-03-15', source: 'ServiceNow', resolutionTime: 6, description: 'Daily automated reports are not being delivered to stakeholders via email.', activityLog: ['Ticket created by Charlie Davis on 2023-03-14', 'Investigated by BI team on 2023-03-14', 'Issue resolved and ticket closed on 2023-03-15'] },
      ]);
    }, 1000);
  });
};

export const fetchTeamTickets = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 101, title: 'Optimize query performance', assignedTo: 'John Doe', status: 'In Progress', priority: 'High', createdDate: '2023-03-10' },
        { id: 102, title: 'Update data model documentation', assignedTo: 'Jane Smith', status: 'Open', priority: 'Medium', createdDate: '2023-03-12' },
        { id: 103, title: 'Investigate data discrepancy', assignedTo: 'Bob Johnson', status: 'Open', priority: 'High', createdDate: '2023-03-13' },
        { id: 104, title: 'Set up new BI tool', assignedTo: 'Alice Brown', status: 'In Progress', priority: 'Medium', createdDate: '2023-03-14' },
        { id: 105, title: 'Create data quality dashboard', assignedTo: 'Charlie Davis', status: 'Open', priority: 'Low', createdDate: '2023-03-15' },
      ]);
    }, 1000);
  });
};

export const fetchUnifiedTickets = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 'JIRA-1001', title: 'Data ingestion failure', status: 'Open', priority: 'High', assignedTo: 'John Doe', source: 'JIRA', createdDate: '2023-03-15' },
        { id: 'SN-2002', title: 'Report generation error', status: 'In Progress', priority: 'Medium', assignedTo: 'Jane Smith', source: 'ServiceNow', createdDate: '2023-03-16' },
        { id: 'AZ-3003', title: 'Pipeline optimization request', status: 'Open', priority: 'Low', assignedTo: 'Bob Johnson', source: 'Azure DevOps', createdDate: '2023-03-17' },
        { id: 'JIRA-1002', title: 'Data quality alert', status: 'Closed', priority: 'High', assignedTo: 'Alice Brown', source: 'JIRA', createdDate: '2023-03-14' },
        { id: 'SN-2003', title: 'Dashboard access issue', status: 'In Progress', priority: 'Medium', assignedTo: 'Charlie Davis', source: 'ServiceNow', createdDate: '2023-03-18' },
      ]);
    }, 1000);
  });
};

export const fetchAIProjects = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 1, name: 'Customer Churn Prediction', status: 'Active', type: 'Classification Model', lastUpdated: '2023-03-15 10:30 AM' },
        { id: 2, name: 'Sales Forecasting', status: 'Deployed', type: 'Regression Model', lastUpdated: '2023-03-16 02:15 PM' },
        { id: 3, name: 'Sentiment Analysis', status: 'Needs Attention', type: 'Natural Language Processing', lastUpdated: '2023-03-17 09:45 AM' },
        { id: 4, name: 'Image Recognition', status: 'Active', type: 'Computer Vision', lastUpdated: '2023-03-18 11:20 AM' },
        { id: 5, name: 'Fraud Detection', status: 'Deployed', type: 'Anomaly Detection', lastUpdated: '2023-03-19 03:30 PM' },
      ]);
    }, 1000);
  });
};

export const fetchProjectDetails = async (id) => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: id,
        name: 'Customer Churn Prediction',
        status: 'Active',
        description: 'This project aims to predict customer churn using historical customer data and behavior patterns.',
        algorithm: 'Random Forest',
        datasets: ['Customer Demographics', 'Transaction History', 'Support Tickets'],
        accuracy: 85,
        confusionMatrix: [
          { name: 'True Negative', truePositive: 0, falsePositive: 30 },
          { name: 'False Negative', truePositive: 20, falsePositive: 0 },
          { name: 'False Positive', truePositive: 0, falsePositive: 15 },
          { name: 'True Positive', truePositive: 35, falsePositive: 0 },
        ],
        rocCurve: [
          { fpr: 0, tpr: 0 },
          { fpr: 0.1, tpr: 0.4 },
          { fpr: 0.3, tpr: 0.7 },
          { fpr: 0.5, tpr: 0.9 },
          { fpr: 0.8, tpr: 0.95 },
          { fpr: 1, tpr: 1 },
        ],
        versions: [
          { number: '1.0', dateCreated: '2023-02-01', changeSummary: 'Initial model deployment' },
          { number: '1.1', dateCreated: '2023-02-15', changeSummary: 'Improved feature engineering' },
          { number: '1.2', dateCreated: '2023-03-01', changeSummary: 'Hyperparameter tuning' },
        ],
      });
    }, 1000);
  });
};

export const fetchDatabricksModels = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 1, name: 'Customer Segmentation', type: 'Clustering', version: '2.1', lastUpdated: '2023-03-15', databricksUrl: 'https://databricks.com' },
        { id: 2, name: 'Product Recommendation', type: 'Collaborative Filtering', version: '1.5', lastUpdated: '2023-03-16', databricksUrl: 'https://databricks.com' },
        { id: 3, name: 'Time Series Forecasting', type: 'ARIMA', version: '3.0', lastUpdated: '2023-03-17', databricksUrl: 'https://databricks.com' },
        { id: 4, name: 'Text Classification', type: 'NLP', version: '2.2', lastUpdated: '2023-03-18', databricksUrl: 'https://databricks.com' },
        { id: 5, name: 'Anomaly Detection', type: 'Isolation Forest', version: '1.8', lastUpdated: '2023-03-19', databricksUrl: 'https://databricks.com' },
      ]);
    }, 1000);
  });
};

// ... (keep all other existing functions)



export const fetchReports = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          name: 'Sales Performance Dashboard',
          description: 'Overview of global sales performance and trends',
          thumbnail: '/placeholder.svg',
          lastModified: '2023-03-15',
          powerBiUrl: 'https://app.powerbi.com/report1',
        },
        {
          id: 2,
          name: 'Financial Analysis Report',
          description: 'Detailed financial analysis including revenue, expenses, and profitability',
          thumbnail: '/placeholder.svg',
          lastModified: '2023-03-16',
          powerBiUrl: 'https://app.powerbi.com/report2',
        },
        {
          id: 3,
          name: 'Operational Efficiency Metrics',
          description: 'Key metrics for measuring and improving operational efficiency',
          thumbnail: '/placeholder.svg',
          lastModified: '2023-03-17',
          powerBiUrl: 'https://app.powerbi.com/report3',
        },
      ]);
    }, 1000);
  });
};

export const fetchSemanticModels = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          name: 'Global Sales Model',
          description: 'Comprehensive model for analyzing global sales data',
          associatedReports: ['Sales Performance Dashboard', 'Regional Sales Analysis'],
          owner: 'John Doe (john.doe@example.com)',
        },
        {
          id: 2,
          name: 'Financial Planning Model',
          description: 'Model for financial planning and forecasting',
          associatedReports: ['Financial Analysis Report', 'Budget vs Actual'],
          owner: 'Jane Smith (jane.smith@example.com)',
        },
        {
          id: 3,
          name: 'Supply Chain Analytics Model',
          description: 'Model for analyzing supply chain efficiency and performance',
          associatedReports: ['Operational Efficiency Metrics', 'Supplier Performance'],
          owner: 'Mike Johnson (mike.johnson@example.com)',
        },
      ]);
    }, 1000);
  });
};

export const fetchDatasets = async () => {
  // Simulated API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          name: 'Customer Demographics',
          description: 'Comprehensive dataset containing customer information including age, gender, location, and purchase history.',
          owner: 'John Doe',
          lastUpdated: '2023-03-15',
          accessLevel: 'granted',
          recordCount: 100000,
          refreshFrequency: 'Daily',
          qualityScore: 9,
          sampleData: {
            headers: ['CustomerID', 'Age', 'Gender', 'Location'],
            rows: [
              [1001, 35, 'Male', 'New York'],
              [1002, 28, 'Female', 'Los Angeles'],
              [1003, 42, 'Female', 'Chicago'],
            ]
          },
          lineage: {
            nodes: [
              { id: 'CRM', size: 24, color: '#97e3d5' },
              { id: 'ETL', size: 24, color: '#61cdbb' },
              { id: 'CustomerDemographics', size: 32, color: '#e8c1a0' },
            ],
            links: [
              { source: 'CRM', target: 'ETL', distance: 80 },
              { source: 'ETL', target: 'CustomerDemographics', distance: 80 },
            ]
          },
          fields: [
            { name: 'CustomerID', type: 'Integer', description: 'Unique identifier for each customer' },
            { name: 'Age', type: 'Integer', description: 'Customer\'s age in years' },
            { name: 'Gender', type: 'String', description: 'Customer\'s gender' },
            { name: 'Location', type: 'String', description: 'Customer\'s city of residence' },
          ],
          qualityMetrics: {
            completeness: 99,
            uniqueness: 100,
            validity: 98,
          },
          tags: ['Customer', 'Demographics', 'CRM Data'],
        },
        {
          id: 2,
          name: 'Sales Transactions',
          description: 'Detailed record of all sales transactions including product information, quantities, and prices.',
          owner: 'Jane Smith',
          lastUpdated: '2023-03-16',
          accessLevel: 'restricted',
          recordCount: 500000,
          refreshFrequency: 'Hourly',
          qualityScore: 8,
          sampleData: {
            headers: ['TransactionID', 'Date', 'ProductID', 'Quantity', 'Price'],
            rows: [
              [10001, '2023-03-15', 'P001', 2, 49.99],
              [10002, '2023-03-15', 'P002', 1, 29.99],
              [10003, '2023-03-16', 'P003', 3, 19.99],
            ]
          },
          lineage: {
            nodes: [
              { id: 'POS', size: 24, color: '#97e3d5' },
              { id: 'ETL', size: 24, color: '#61cdbb' },
              { id: 'SalesTransactions', size: 32, color: '#e8c1a0' },
            ],
            links: [
              { source: 'POS', target: 'ETL', distance: 80 },
              { source: 'ETL', target: 'SalesTransactions', distance: 80 },
            ]
          },
          fields: [
            { name: 'TransactionID', type: 'Integer', description: 'Unique identifier for each transaction' },
            { name: 'Date', type: 'Date', description: 'Date of the transaction' },
            { name: 'ProductID', type: 'String', description: 'Unique identifier for the product' },
            { name: 'Quantity', type: 'Integer', description: 'Number of items purchased' },
            { name: 'Price', type: 'Decimal', description: 'Price per item' },
          ],
          qualityMetrics: {
            completeness: 100,
            uniqueness: 100,
            validity: 99,
          },
          tags: ['Sales', 'Transactions', 'Financial Data'],
        },
        {
          id: 3,
          name: "Sales Performance Dashboard",
          type: "Dashboard",
          description: "Overview of global sales performance and trends",
          owner: "Sarah Johnson",
          lastUpdated: "2023-04-01",
          accessLevel: "granted",
          thumbnail: "/placeholder.svg",
          powerBiUrl: "https://app.powerbi.com/report1",
        },
        {
          id: 4,
          name: "Customer Churn Prediction",
          type: "AI Model",
          description: "Machine learning model to predict customer churn",
          owner: "Alex Chen",
          lastUpdated: "2023-03-28",
          accessLevel: "restricted",
          accuracy: "85%",
          algorithm: "Random Forest",
        },
        {
          id: 5,
          name: "Global Sales Model",
          type: "Semantic Model",
          description: "Comprehensive model for analyzing global sales data",
          owner: "John Doe",
          lastUpdated: "2023-03-25",
          accessLevel: "granted",
          associatedReports: ["Sales Performance Dashboard", "Regional Sales Analysis"],
        },
        // ... (keep other existing entries)
      ]);
    }, 1000);
  });
};

// ... (keep other existing functions)