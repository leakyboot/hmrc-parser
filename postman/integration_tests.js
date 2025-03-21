// Integration test script for UK Tax Parser API
// Designed to work with Tesseract OCR in test environment

// Global variables
let documentId;
let accessToken;

// Test suites
const authTests = {
    validateToken: () => {
        pm.test("Token structure is valid", () => {
            const jsonData = pm.response.json();
            pm.expect(jsonData).to.have.property('access_token');
            pm.expect(jsonData.token_type).to.equal('bearer');
            accessToken = jsonData.access_token;
        });
    }
};

const documentTests = {
    validateUpload: () => {
        pm.test("Document upload successful", () => {
            const jsonData = pm.response.json();
            pm.expect(jsonData.status).to.equal('success');
            pm.expect(jsonData).to.have.property('document_id');
            documentId = jsonData.document_id;
        });

        pm.test("OCR data extraction successful", () => {
            const jsonData = pm.response.json();
            pm.expect(jsonData).to.have.property('data');
            const data = jsonData.data;
            pm.expect(data).to.have.property('tax_year');
            pm.expect(data).to.have.property('total_pay');
            pm.expect(data).to.have.property('total_tax');
        });
    },

    validateStatus: () => {
        pm.test("Document status is valid", () => {
            const jsonData = pm.response.json();
            pm.expect(jsonData).to.have.property('status');
            pm.expect(jsonData).to.have.property('document_id');
            pm.expect(jsonData).to.have.property('last_updated');
            pm.expect(['processing', 'completed', 'failed']).to.include(jsonData.status);
        });
    },

    validateData: (documentType) => {
        pm.test("Document data is complete", () => {
            const jsonData = pm.response.json();
            
            // Common fields for all document types
            pm.expect(jsonData).to.have.property('tax_year');
            pm.expect(jsonData).to.have.property('total_income');
            pm.expect(jsonData).to.have.property('tax_paid');
            pm.expect(jsonData).to.have.property('ni_number');
            pm.expect(jsonData).to.have.property('employer_name');

            // P45-specific fields
            if (documentType === 'P45') {
                pm.expect(jsonData).to.have.property('leaving_date');
            }

            // Validate data types
            pm.expect(Number(jsonData.total_income)).to.be.a('number');
            pm.expect(Number(jsonData.tax_paid)).to.be.a('number');
            pm.expect(jsonData.ni_number).to.match(/^[A-Z]{2}(?:\d{2}){3}[A-Z]$/);
        });
    },

    validateDelete: () => {
        pm.test("Document deletion successful", () => {
            const jsonData = pm.response.json();
            pm.expect(jsonData.status).to.equal('Document deleted successfully');
        });
    }
};

const errorTests = {
    validateInvalidFileType: () => {
        pm.test("Invalid file type rejected", () => {
            pm.response.to.have.status(400);
            const jsonData = pm.response.json();
            pm.expect(jsonData.detail).to.include('Invalid file format');
        });
    },

    validateUnauthorized: () => {
        pm.test("Unauthorized access rejected", () => {
            pm.response.to.have.status(401);
        });
    },

    validateNotFound: () => {
        pm.test("Non-existent document handled", () => {
            pm.response.to.have.status(404);
        });
    }
};

// Test environment validation
const validateTestEnvironment = () => {
    pm.test("Test environment configuration", () => {
        pm.expect(pm.environment.get('base_url')).to.not.be.empty;
        pm.expect(pm.environment.get('username')).to.not.be.empty;
        pm.expect(pm.environment.get('password')).to.not.be.empty;
    });

    pm.test("OCR engine configuration", () => {
        // Default to Tesseract in test environment
        const headers = pm.response.headers;
        const serverConfig = headers.get('X-OCR-Engine') || 'tesseract';
        pm.expect(serverConfig.toLowerCase()).to.equal('tesseract');
    });
};

// Export test functions for use in Postman collection
module.exports = {
    authTests,
    documentTests,
    errorTests,
    validateTestEnvironment
};
