import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    company_size: '',
    decision_maker_name: '',
    decision_maker_title: '',
    linkedin_url: '',
    manual_content: ''
  });

  useEffect(() => {
    fetchLeads();
    fetchStats();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/leads`);
      const data = await response.json();
      setLeads(data);
    } catch (error) {
      console.error('Error fetching leads:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/leads/stats/summary`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setFormData({
          company_name: '',
          industry: '',
          company_size: '',
          decision_maker_name: '',
          decision_maker_title: '',
          linkedin_url: '',
          manual_content: ''
        });
        setShowAddForm(false);
        fetchLeads();
        fetchStats();
      }
    } catch (error) {
      console.error('Error creating lead:', error);
    }
    
    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-red-600 bg-red-100';
    if (score >= 5) return 'text-yellow-600 bg-yellow-100';
    return 'text-blue-600 bg-blue-100';
  };

  const getScoreLabel = (score) => {
    if (score >= 8) return 'HOT';
    if (score >= 5) return 'WARM';
    return 'COLD';
  };

  const getColdnessLabel = (score) => {
    if (score <= 3) return 'Very Active';
    if (score <= 6) return 'Moderately Active';
    return 'Low Activity';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Lead Generation System</h1>
              <p className="text-gray-600">AI-powered lead qualification and pain point analysis</p>
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              Add New Lead
            </button>
          </div>
        </div>
      </header>

      {/* Stats Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">{stats.total_leads || 0}</div>
            <div className="text-gray-600">Total Leads</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-red-600">{stats.hot_leads || 0}</div>
            <div className="text-gray-600">Hot Leads (8-10)</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-yellow-600">{stats.warm_leads || 0}</div>
            <div className="text-gray-600">Warm Leads (5-7)</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-blue-600">{stats.cold_leads || 0}</div>
            <div className="text-gray-600">Cold Leads (1-4)</div>
          </div>
        </div>

        {/* Add Lead Form */}
        {showAddForm && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Lead</h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Name *
                    </label>
                    <input
                      type="text"
                      value={formData.company_name}
                      onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Industry
                    </label>
                    <input
                      type="text"
                      value={formData.industry}
                      onChange={(e) => setFormData({...formData, industry: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Size
                    </label>
                    <select
                      value={formData.company_size}
                      onChange={(e) => setFormData({...formData, company_size: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select size</option>
                      <option value="1-10">1-10 employees</option>
                      <option value="11-50">11-50 employees</option>
                      <option value="51-200">51-200 employees</option>
                      <option value="201-1000">201-1000 employees</option>
                      <option value="1000+">1000+ employees</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Decision Maker Name
                    </label>
                    <input
                      type="text"
                      value={formData.decision_maker_name}
                      onChange={(e) => setFormData({...formData, decision_maker_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Decision Maker Title
                    </label>
                    <input
                      type="text"
                      value={formData.decision_maker_title}
                      onChange={(e) => setFormData({...formData, decision_maker_title: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      LinkedIn URL
                    </label>
                    <input
                      type="url"
                      value={formData.linkedin_url}
                      onChange={(e) => setFormData({...formData, linkedin_url: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Manual Content for Analysis
                  </label>
                  <textarea
                    value={formData.manual_content}
                    onChange={(e) => setFormData({...formData, manual_content: e.target.value})}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Paste LinkedIn posts, company information, blog content, or any relevant text for AI analysis..."
                  />
                </div>
                <div className="flex space-x-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-semibold disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Lead'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-md font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Leads List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Pipeline</h3>
            {leads.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg mb-4">No leads yet</div>
                <p className="text-gray-600">Add your first lead to get started with AI-powered analysis</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full table-auto">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold">Company</th>
                      <th className="text-left py-3 px-4 font-semibold">Decision Maker</th>
                      <th className="text-left py-3 px-4 font-semibold">Lead Score</th>
                      <th className="text-left py-3 px-4 font-semibold">Coldness</th>
                      <th className="text-left py-3 px-4 font-semibold">Pain Points</th>
                      <th className="text-left py-3 px-4 font-semibold">Status</th>
                      <th className="text-left py-3 px-4 font-semibold">Created</th>
                      <th className="text-left py-3 px-4 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map((lead) => (
                      <tr key={lead.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-semibold text-gray-900">{lead.company_name}</div>
                            <div className="text-sm text-gray-600">{lead.industry}</div>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium">{lead.decision_maker_name || 'N/A'}</div>
                            <div className="text-sm text-gray-600">{lead.decision_maker_title || 'N/A'}</div>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          {lead.total_lead_score ? (
                            <div className={`inline-flex px-2 py-1 rounded-full text-sm font-semibold ${getScoreColor(lead.total_lead_score)}`}>
                              {lead.total_lead_score} - {getScoreLabel(lead.total_lead_score)}
                            </div>
                          ) : (
                            <span className="text-gray-400">Pending</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          {lead.coldness_score ? (
                            <div>
                              <div className="font-medium">{lead.coldness_score}/10</div>
                              <div className="text-xs text-gray-600">{getColdnessLabel(lead.coldness_score)}</div>
                            </div>
                          ) : (
                            <span className="text-gray-400">N/A</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <div className="text-sm">
                            {lead.pain_points && lead.pain_points.length > 0 ? (
                              <div>
                                <div className="font-medium">{lead.pain_points.length} identified</div>
                                <div className="text-gray-600">
                                  Avg urgency: {(lead.pain_points.reduce((sum, pp) => sum + pp.urgency, 0) / lead.pain_points.length).toFixed(1)}/5
                                </div>
                              </div>
                            ) : (
                              <span className="text-gray-400">None</span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                            lead.analysis_status === 'completed' ? 'bg-green-100 text-green-800' :
                            lead.analysis_status === 'analyzing' ? 'bg-blue-100 text-blue-800' :
                            lead.analysis_status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {lead.analysis_status}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {formatDate(lead.created_at)}
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => setSelectedLead(lead)}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Lead Detail Modal */}
        {selectedLead && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-90vh overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedLead.company_name}</h2>
                    <p className="text-gray-600">{selectedLead.industry} • {selectedLead.company_size}</p>
                  </div>
                  <button
                    onClick={() => setSelectedLead(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Contact Information</h3>
                    <div className="space-y-2">
                      <p><strong>Decision Maker:</strong> {selectedLead.decision_maker_name || 'N/A'}</p>
                      <p><strong>Title:</strong> {selectedLead.decision_maker_title || 'N/A'}</p>
                      <p><strong>LinkedIn:</strong> 
                        {selectedLead.linkedin_url ? (
                          <a href={selectedLead.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-1">
                            View Profile
                          </a>
                        ) : ' N/A'}
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Scoring</h3>
                    <div className="space-y-2">
                      <p><strong>Total Lead Score:</strong> 
                        {selectedLead.total_lead_score ? (
                          <span className={`ml-2 px-2 py-1 rounded text-sm font-semibold ${getScoreColor(selectedLead.total_lead_score)}`}>
                            {selectedLead.total_lead_score} - {getScoreLabel(selectedLead.total_lead_score)}
                          </span>
                        ) : ' Pending'}
                      </p>
                      <p><strong>Coldness Score:</strong> {selectedLead.coldness_score ? `${selectedLead.coldness_score}/10` : 'N/A'}</p>
                      <p><strong>Analysis Status:</strong> 
                        <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                          selectedLead.analysis_status === 'completed' ? 'bg-green-100 text-green-800' :
                          selectedLead.analysis_status === 'analyzing' ? 'bg-blue-100 text-blue-800' :
                          selectedLead.analysis_status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedLead.analysis_status}
                        </span>
                      </p>
                    </div>
                  </div>
                </div>

                {selectedLead.pain_points && selectedLead.pain_points.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">Identified Pain Points</h3>
                    <div className="space-y-3">
                      {selectedLead.pain_points.map((painPoint, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-medium">{painPoint.description}</span>
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                painPoint.urgency >= 4 ? 'bg-red-100 text-red-800' :
                                painPoint.urgency >= 3 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                Urgency: {painPoint.urgency}/5
                              </span>
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                {painPoint.category}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedLead.best_outreach_angle && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">Best Outreach Angle</h3>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-gray-800">{selectedLead.best_outreach_angle}</p>
                    </div>
                  </div>
                )}

                {selectedLead.recent_activity_summary && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">Recent Activity Summary</h3>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <p className="text-gray-800">{selectedLead.recent_activity_summary}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;