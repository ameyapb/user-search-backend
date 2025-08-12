import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [accounts, setAccounts] = useState([]);
  const [filteredAccounts, setFilteredAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedAccount, setSelectedAccount] = useState(null);

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

  const AccountCard = ({ account }) => {
    const isProvider = account.account_type === 'service_provider';

    return (
      <div
        className={`account-card ${isProvider ? 'provider-card' : 'consumer-card'}`}
        onClick={() => handleCardClick(account)}
      >
        <div className="card-header">
          <h3 className="account-name">{account.name}</h3>
          <span className={`account-type ${isProvider ? 'provider-badge' : 'consumer-badge'}`}>
            {isProvider ? 'Provider' : 'Consumer'}
          </span>
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
    </div>
  );
}

export default App;
