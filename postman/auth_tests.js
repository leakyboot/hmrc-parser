// Authentication test suite for UK Tax Parser API
const authTests = {
    // Valid credentials test
    testValidLogin: () => {
        pm.test("Successful login returns valid token", () => {
            const jsonData = pm.response.json();
            
            // Check response structure
            pm.expect(jsonData).to.have.property('access_token');
            pm.expect(jsonData).to.have.property('token_type');
            pm.expect(jsonData.token_type).to.equal('bearer');
            
            // Validate token format (JWT has 3 parts separated by dots)
            const token = jsonData.access_token;
            pm.expect(token.split('.')).to.have.lengthOf(3);
            
            // Store token for subsequent requests
            pm.environment.set('access_token', token);
        });
    },

    // Invalid credentials test
    testInvalidLogin: () => {
        pm.test("Invalid credentials are rejected", () => {
            pm.response.to.have.status(401);
            const jsonData = pm.response.json();
            pm.expect(jsonData.detail).to.include('Incorrect username or password');
        });
    },

    // Token expiration test
    testTokenExpiration: () => {
        pm.test("Token expiration is 30 minutes", () => {
            const token = pm.response.json().access_token;
            const payload = JSON.parse(atob(token.split('.')[1]));
            
            const issueTime = payload.iat;
            const expiryTime = payload.exp;
            
            // Verify 30-minute expiration
            pm.expect(expiryTime - issueTime).to.equal(30 * 60); // 30 minutes in seconds
        });
    },

    // Role-based access test
    testRoleBasedAccess: () => {
        const token = pm.environment.get('access_token');
        const payload = JSON.parse(atob(token.split('.')[1]));
        
        pm.test("Token contains role information", () => {
            pm.expect(payload).to.have.property('role');
            pm.expect(['admin', 'user', 'readonly']).to.include(payload.role);
        });
    },

    // Missing token test
    testMissingToken: () => {
        pm.test("Protected endpoint requires token", () => {
            pm.response.to.have.status(401);
            const jsonData = pm.response.json();
            pm.expect(jsonData.detail).to.include('Not authenticated');
        });
    }
};

// Export test functions
module.exports = authTests;
