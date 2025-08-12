import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [accounts, setAccounts] = useState([]);
  const [filteredAccounts, setFilteredAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(null); // 'provider' or 'consumer'

  // Fetch all accounts on component mount
  useEffect(() => {
    fetchAccounts();
  }, []);

  // Filter accounts when search term changes
  useEffect(() => {
    filterAccounts();
  }, [searchTerm, accounts]);

  const fetchAccounts = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/v1/');
      const data = await response.json();
      console.log('API Response:', data); // Debug log
      console.log('Sample account availability:', data.data?.[0]?.availability); // Debug availability field

      // Handle different response formats
      let accountsArray = data;
      if (data && typeof data === 'object' && !Array.isArray(data)) {
        // If response has accounts property
        if (data.accounts) {
          accountsArray = data.accounts;
        }
        // If response has data property
        else if (data.data) {
          accountsArray = data.data;
        }
        // If it's a single object, wrap it in array
        else {
          accountsArray = [data];
        }
      }

      // Ensure it's an array
      if (!Array.isArray(accountsArray)) {
        console.warn('Expected array but got:', typeof accountsArray, accountsArray);
        accountsArray = [];
      }

      setAccounts(accountsArray);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      setAccounts([]); // Set empty array on error
      setLoading(false);
    }
  };

  const filterAccounts = () => {
    if (!searchTerm.trim()) {
      setFilteredAccounts(accounts);
      return;
    }

    const filtered = accounts.filter(account => {
      const searchLower = searchTerm.toLowerCase();

      // Search in name
      if (account.name?.toLowerCase().includes(searchLower)) return true;

      // Search in tags
      if (account.tags?.some(tag => tag.toLowerCase().includes(searchLower))) return true;

      // Search in account type
      if (account.account_type?.toLowerCase().includes(searchLower)) return true;

      // Search in email
      if (account.email?.toLowerCase().includes(searchLower)) return true;

      return false;
    });

    setFilteredAccounts(filtered);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleCardClick = (account) => {
    setSelectedAccount(account);
  };

  const closeModal = () => {
    setSelectedAccount(null);
  };

  const closeCreateForm = () => {
    setShowCreateForm(null);
  };

  const handleDelete = async (accountId, accountType, e) => {
    e.stopPropagation(); // Prevent card click

    if (!window.confirm('Are you sure you want to delete this account?')) {
      return;
    }

    try {
      const endpoint = accountType === 'service_provider'
        ? `http://localhost:3000/api/v1/providers/${accountId}`
        : `http://localhost:3000/api/v1/consumers/${accountId}`;

      const response = await fetch(endpoint, {
        method: 'DELETE'
      });

      if (response.ok) {
        // Refresh the accounts list
        fetchAccounts();
      } else {
        alert('Failed to delete account');
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Error deleting account');
    }
  };

  const handleCreateSubmit = async (formData, accountType) => {
    try {
      const endpoint = accountType === 'provider'
        ? 'http://localhost:3000/api/v1/providers'
        : 'http://localhost:3000/api/v1/consumers';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        // Refresh the accounts list and close form
        fetchAccounts();
        setShowCreateForm(null);
      } else {
        alert('Failed to create account');
      }
    } catch (error) {
      console.error('Error creating account:', error);
      alert('Error creating account');
    }
  };

  const AccountCard = ({ account }) => {
    const isProvider = account.account_type === 'service_provider';

    return (
      <div
        className={`account-card ${isProvider ? 'provider-card' : 'consumer-card'}`}
        onClick={() => handleCardClick(account)}
      >
        <div className="card-header">
          <h3 className="account-name">{account.name}</h3>
          <div className="card-header-right">
            <span className={`account-type ${isProvider ? 'provider-badge' : 'consumer-badge'}`}>
              {isProvider ? 'Provider' : 'Consumer'}
            </span>
            <button
              className="delete-button"
              onClick={(e) => handleDelete(account.id, account.account_type, e)}
              title="Delete account"
            >
              ×
            </button>
          </div>
        </div>

        <div className="account-details">
          <p className="account-email">{account.email}</p>

          {/* Provider specific info */}
          {isProvider && account.hourly_rate && (
            <p className="hourly-rate">${account.hourly_rate}/hour</p>
          )}

          {isProvider && account.availability && (
            <p className="availability">
              {typeof account.availability === 'string'
                ? account.availability
                : typeof account.availability === 'object'
                  ? `${account.availability.weekdays || ''} ${account.availability.weekends || ''}`.trim() || 'Available'
                  : 'Available'
              }
            </p>
          )}

          {/* Consumer specific info */}
          {!isProvider && account.preferred_budget && (
            <p className="budget">Budget: ${account.preferred_budget}</p>
          )}

          {/* Address */}
          {account.address && (
            <p className="address">
              {account.address.city}
              {account.address.street && `, ${account.address.street}`}
            </p>
          )}
        </div>

        {/* Tags */}
        {account.tags && account.tags.length > 0 && (
          <div className="tags">
            {account.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="tag">
                {tag}
              </span>
            ))}
            {account.tags.length > 3 && (
              <span className="tag-more">+{account.tags.length - 3}</span>
            )}
          </div>
        )}
      </div>
    );
  };

  const CreateForm = ({ accountType, onSubmit, onClose }) => {
    const [formData, setFormData] = useState({
      name: '',
      email: '',
      street: '',
      city: '',
      tags: '',
      ...(accountType === 'provider' ? {
        hourly_rate: '',
        availability: ''
      } : {
        preferred_budget: ''
      })
    });

    const handleInputChange = (e) => {
      const { name, value } = e.target;
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    };

    const handleSubmit = (e) => {
      e.preventDefault();

      // Format the data for the API
      const submitData = {
        name: formData.name,
        email: formData.email,
        address: {
          street: formData.street,
          city: formData.city
        },
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      if (accountType === 'provider') {
        if (formData.hourly_rate) submitData.hourly_rate = parseFloat(formData.hourly_rate);
        if (formData.availability) submitData.availability = formData.availability;
      } else {
        if (formData.preferred_budget) submitData.preferred_budget = parseFloat(formData.preferred_budget);
      }

      onSubmit(submitData, accountType);
    };

    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content create-form" onClick={(e) => e.stopPropagation()}>
          <button className="close-button" onClick={onClose}>×</button>

          <div className="modal-header">
            <h2>Add New {accountType === 'provider' ? 'Provider' : 'Consumer'}</h2>
          </div>

          <form onSubmit={handleSubmit} className="create-form-body">
            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Street</label>
              <input
                type="text"
                name="street"
                value={formData.street}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>City</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
              />
            </div>

            {accountType === 'provider' && (
              <>
                <div className="form-group">
                  <label>Hourly Rate ($)</label>
                  <input
                    type="number"
                    name="hourly_rate"
                    value={formData.hourly_rate}
                    onChange={handleInputChange}
                    step="0.01"
                  />
                </div>

                <div className="form-group">
                  <label>Availability</label>
                  <input
                    type="text"
                    name="availability"
                    value={formData.availability}
                    onChange={handleInputChange}
                    placeholder="e.g., Mon-Fri 9AM-5PM"
                  />
                </div>
              </>
            )}

            {accountType === 'consumer' && (
              <div className="form-group">
                <label>Preferred Budget ($)</label>
                <input
                  type="number"
                  name="preferred_budget"
                  value={formData.preferred_budget}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>
            )}

            <div className="form-group">
              <label>Tags (comma-separated)</label>
              <input
                type="text"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="e.g., plumber, emergency, residential"
              />
            </div>

            <div className="form-actions">
              <button type="button" onClick={onClose} className="cancel-button">
                Cancel
              </button>
              <button type="submit" className="submit-button">
                Create {accountType === 'provider' ? 'Provider' : 'Consumer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const AccountModal = ({ account, onClose }) => {
    if (!account) return null;

    const isProvider = account.account_type === 'service_provider';

    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <button className="close-button" onClick={onClose}>×</button>

          <div className="modal-header">
            <h2>{account.name}</h2>
            <span className={`account-type ${isProvider ? 'provider-badge' : 'consumer-badge'}`}>
              {isProvider ? 'Service Provider' : 'Service Consumer'}
            </span>
          </div>

          <div className="modal-body">
            <p><strong>Email:</strong> {account.email}</p>

            {account.address && (
              <p><strong>Address:</strong> {account.address.street}, {account.address.city}</p>
            )}

            {isProvider && account.hourly_rate && (
              <p><strong>Hourly Rate:</strong> ${account.hourly_rate}</p>
            )}

            {isProvider && account.availability && (
              <p><strong>Availability:</strong> {
                typeof account.availability === 'string'
                  ? account.availability
                  : typeof account.availability === 'object'
                    ? `${account.availability.weekdays || ''} ${account.availability.weekends || ''}`.trim() || 'Available'
                    : 'Available'
              }</p>
            )}

            {!isProvider && account.preferred_budget && (
              <p><strong>Preferred Budget:</strong> ${account.preferred_budget}</p>
            )}

            {account.tags && account.tags.length > 0 && (
              <div>
                <strong>Tags:</strong>
                <div className="modal-tags">
                  {account.tags.map((tag, index) => (
                    <span key={index} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Service history for consumers */}
            {!isProvider && account.service_history && account.service_history.length > 0 && (
              <div>
                <strong>Service History:</strong>
                <div className="service-history">
                  {account.service_history.map((service, index) => (
                    <div key={index} className="service-item">
                      <p>{service.service} - ${service.cost}</p>
                      <small>Provider: {service.provider} | Date: {service.date}</small>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <h1 className="app-title">Service Marketplace</h1>
        <p className="app-subtitle">Find service providers and consumers</p>
      </header>

      {/* Add Account Buttons */}
      <div className="add-buttons">
        <button
          className="add-button provider-button"
          onClick={() => setShowCreateForm('provider')}
        >
          + Add Provider
        </button>
        <button
          className="add-button consumer-button"
          onClick={() => setShowCreateForm('consumer')}
        >
          + Add Consumer
        </button>
      </div>

      {/* Search Bar */}
      <div className="search-container">
        <input
          type="text"
          className="search-bar"
          placeholder="Search providers and consumers..."
          value={searchTerm}
          onChange={handleSearchChange}
        />
      </div>

      {/* Results Count */}
      <div className="results-info">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <p>{filteredAccounts.length} results found</p>
        )}
      </div>

      {/* Results Grid */}
      <div className="results-grid">
        {loading ? (
          <div className="loading">Loading accounts...</div>
        ) : filteredAccounts.length === 0 ? (
          <div className="no-results">
            {searchTerm ? 'No accounts match your search.' : 'No accounts found.'}
          </div>
        ) : (
          filteredAccounts.map((account) => (
            <AccountCard key={account.id} account={account} />
          ))
        )}
      </div>

      {/* Modal for account details */}
      {selectedAccount && (
        <AccountModal account={selectedAccount} onClose={closeModal} />
      )}

      {/* Create form modal */}
      {showCreateForm && (
        <CreateForm
          accountType={showCreateForm}
          onSubmit={handleCreateSubmit}
          onClose={closeCreateForm}
        />
      )}
    </div>
  );
}

export default App;
