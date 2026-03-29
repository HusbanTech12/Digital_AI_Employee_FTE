/**
 * Odoo MCP Server
 * 
 * Model Context Protocol server for Odoo accounting integration.
 * Uses Odoo's JSON-RPC API for invoice management, payments, and financial reporting.
 * 
 * Gold Tier Feature: Accounting system integration via MCP
 * 
 * Usage:
 *   npx @modelcontextprotocol/sdk odoo-mcp
 * 
 * Configuration:
 *   Set environment variables or use .env file:
 *   - ODOO_URL: Odoo server URL (e.g., http://localhost:8069)
 *   - ODOO_DB: Database name
 *   - ODOO_USERNAME: Odoo username/email
 *   - ODOO_PASSWORD: Odoo password or API key
 *   - ODOO_COMPANY_ID: Company ID (optional)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import { readFileSync } from 'fs';
import { join } from 'path';

// Configuration
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || 'odoo';
const ODOO_USERNAME = process.env.ODOO_USERNAME || '';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || '';
const ODOO_COMPANY_ID = process.env.ODOO_COMPANY_ID || '';

// Logging
function log(level, message) {
  const timestamp = new Date().toISOString();
  console.error(`[${timestamp}] [${level}] ${message}`);
}

/**
 * Odoo JSON-RPC Client
 */
class OdooClient {
  constructor(url, db, username, password) {
    this.url = url;
    this.db = db;
    this.username = username;
    this.password = password;
    this.uid = null;
  }

  async authenticate() {
    try {
      const response = await axios.post(`${this.url}/jsonrpc`, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'common',
          method: 'authenticate',
          args: [this.db, this.username, this.password, {}]
        },
        id: 1
      });

      if (response.data.result) {
        this.uid = response.data.result.uid;
        log('INFO', `Odoo authenticated as user ${this.uid}`);
        return true;
      }
      return false;
    } catch (error) {
      log('ERROR', `Odoo authentication failed: ${error.message}`);
      return false;
    }
  }

  async execute(model, method, args = [], kwargs = {}) {
    try {
      if (!this.uid) {
        await this.authenticate();
      }

      const response = await axios.post(`${this.url}/jsonrpc`, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute',
          args: [this.db, this.uid, this.password, model, method, ...args],
          kwargs: kwargs
        },
        id: Date.now()
      });

      return response.data.result;
    } catch (error) {
      log('ERROR', `Odoo execute failed: ${error.message}`);
      throw error;
    }
  }

  async searchRead(model, domain, fields = [], limit = 80) {
    return await this.execute(model, 'search_read', [domain], {
      fields: fields,
      limit: limit
    });
  }

  async create(model, values) {
    return await this.execute(model, 'create', [values]);
  }

  async write(model, id, values) {
    return await this.execute(model, 'write', [[id], values]);
  }

  async unlink(model, id) {
    return await this.execute(model, 'unlink', [[id]]);
  }
}

// Initialize Odoo client
let odooClient = null;

function getOdooClient() {
  if (!odooClient) {
    odooClient = new OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD);
  }
  return odooClient;
}

/**
 * Tool: Create Invoice
 */
async function createInvoice(params) {
  const {
    partner_id,
    invoice_date,
    due_date,
    invoice_line_ids,
    payment_term_id,
    move_type = 'out_invoice'
  } = params;

  log('INFO', `Creating invoice for partner ${partner_id}`);

  try {
    const client = getOdooClient();

    // Create invoice
    const invoiceValues = {
      partner_id: partner_id,
      invoice_date: invoice_date,
      invoice_date_due: due_date,
      move_type: move_type,
      invoice_line_ids: invoice_line_ids || [],
    };

    if (payment_term_id) {
      invoiceValues.invoice_payment_term_id = payment_term_id;
    }

    const invoiceId = await client.create('account.move', invoiceValues);

    log('INFO', `Invoice created with ID: ${invoiceId}`);

    return {
      success: true,
      invoice_id: invoiceId,
      status: 'draft',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    log('ERROR', `Failed to create invoice: ${error.message}`);
    throw error;
  }
}

/**
 * Tool: Get Invoices
 */
async function getInvoices(params) {
  const {
    partner_id,
    state = ['draft', 'posted'],
    limit = 10
  } = params;

  log('INFO', `Fetching invoices (limit: ${limit})`);

  try {
    const client = getOdooClient();

    const domain = [];
    if (partner_id) {
      domain.push(['partner_id', '=', partner_id]);
    }
    if (state) {
      domain.push(['state', 'in', state]);
    }

    const invoices = await client.searchRead(
      'account.move',
      domain,
      ['id', 'name', 'partner_id', 'amount_total', 'amount_due', 'state', 'invoice_date', 'invoice_date_due'],
      limit
    );

    log('INFO', `Found ${invoices.length} invoices`);

    return {
      success: true,
      count: invoices.length,
      invoices: invoices.map(inv => ({
        id: inv.id,
        number: inv.name,
        partner: inv.partner_id?.[1] || 'Unknown',
        amount_total: inv.amount_total,
        amount_due: inv.amount_due,
        state: inv.state,
        invoice_date: inv.invoice_date,
        due_date: inv.invoice_date_due,
      })),
    };
  } catch (error) {
    log('ERROR', `Failed to get invoices: ${error.message}`);
    throw error;
  }
}

/**
 * Tool: Validate Invoice
 */
async function validateInvoice(params) {
  const { invoice_id } = params;

  log('INFO', `Validating invoice ${invoice_id}`);

  try {
    const client = getOdooClient();

    // Post the invoice (validate)
    await client.execute('account.move', 'action_post', [[invoice_id]]);

    log('INFO', `Invoice ${invoice_id} validated`);

    return {
      success: true,
      invoice_id: invoice_id,
      status: 'posted',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    log('ERROR', `Failed to validate invoice: ${error.message}`);
    throw error;
  }
}

/**
 * Tool: Register Payment
 */
async function registerPayment(params) {
  const {
    invoice_id,
    amount,
    payment_date,
    payment_method = 'manual'
  } = params;

  log('INFO', `Registering payment for invoice ${invoice_id}`);

  try {
    const client = getOdooClient();

    // Create payment registration
    const paymentValues = {
      move_ids: [[6, 0, [invoice_id]]],
      payment_type: 'inbound',
      amount: amount,
      date: payment_date,
      payment_method_line_id: payment_method,
    };

    const paymentId = await client.create('account.payment.register', paymentValues);
    
    // Create the actual payment
    await client.execute('account.payment.register', 'create_payments', [[paymentId]]);

    log('INFO', `Payment registered for invoice ${invoice_id}`);

    return {
      success: true,
      payment_id: paymentId,
      amount: amount,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    log('ERROR', `Failed to register payment: ${error.message}`);
    throw error;
  }
}

/**
 * Tool: Get Financial Summary
 */
async function getFinancialSummary(params) {
  const {
    period = 'month'
  } = params;

  log('INFO', `Getting financial summary for ${period}`);

  try {
    const client = getOdooClient();

    // Get total receivables
    const receivables = await client.searchRead(
      'account.move',
      [['move_type', '=', 'out_invoice'], ['state', '=', 'posted']],
      ['amount_total', 'amount_residual'],
      1000
    );

    const totalReceivables = receivables.reduce((sum, inv) => sum + (inv.amount_residual || 0), 0);
    const totalRevenue = receivables.reduce((sum, inv) => sum + (inv.amount_total || 0), 0);

    // Get total payables
    const payables = await client.searchRead(
      'account.move',
      [['move_type', '=', 'in_invoice'], ['state', '=', 'posted']],
      ['amount_total', 'amount_residual'],
      1000
    );

    const totalPayables = payables.reduce((sum, inv) => sum + (inv.amount_residual || 0), 0);
    const totalExpenses = payables.reduce((sum, inv) => sum + (inv.amount_total || 0), 0);

    return {
      success: true,
      summary: {
        total_receivables: totalReceivables,
        total_payables: totalPayables,
        total_revenue: totalRevenue,
        total_expenses: totalExpenses,
        net_position: totalReceivables - totalPayables,
        invoice_count: receivables.length,
        bill_count: payables.length,
      },
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    log('ERROR', `Failed to get financial summary: ${error.message}`);
    throw error;
  }
}

/**
 * Tool: Get Partners
 */
async function getPartners(params) {
  const {
    search_term,
    limit = 20
  } = params;

  log('INFO', `Searching partners: ${search_term || 'all'}`);

  try {
    const client = getOdooClient();

    const domain = search_term ? [
      ['|', ['name', 'ilike', search_term], ['email', 'ilike', search_term]]
    ] : [];

    const partners = await client.searchRead(
      'res.partner',
      domain,
      ['id', 'name', 'email', 'phone', 'customer_rank', 'supplier_rank'],
      limit
    );

    return {
      success: true,
      count: partners.length,
      partners: partners.map(p => ({
        id: p.id,
        name: p.name,
        email: p.email,
        phone: p.phone,
        is_customer: p.customer_rank > 0,
        is_supplier: p.supplier_rank > 0,
      })),
    };
  } catch (error) {
    log('ERROR', `Failed to get partners: ${error.message}`);
    throw error;
  }
}

// Create MCP server
const server = new Server(
  {
    name: 'odoo-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'create_invoice',
        description: 'Create a new customer invoice in Odoo. Requires approval before posting.',
        inputSchema: {
          type: 'object',
          properties: {
            partner_id: {
              type: 'integer',
              description: 'Customer/partner ID',
            },
            invoice_date: {
              type: 'string',
              description: 'Invoice date (YYYY-MM-DD)',
            },
            due_date: {
              type: 'string',
              description: 'Due date (YYYY-MM-DD)',
            },
            invoice_line_ids: {
              type: 'array',
              description: 'Invoice lines with products, quantities, prices',
              items: {
                type: 'object',
                properties: {
                  product_id: { type: 'integer' },
                  name: { type: 'string' },
                  quantity: { type: 'number' },
                  price_unit: { type: 'number' },
                },
              },
            },
            move_type: {
              type: 'string',
              description: 'Invoice type: out_invoice, in_invoice, out_refund, in_refund',
            },
          },
          required: ['partner_id', 'invoice_date'],
        },
      },
      {
        name: 'get_invoices',
        description: 'Fetch invoices from Odoo with optional filtering',
        inputSchema: {
          type: 'object',
          properties: {
            partner_id: {
              type: 'integer',
              description: 'Filter by customer/partner ID',
            },
            state: {
              type: 'array',
              description: 'Filter by state: draft, posted, cancel',
              items: { type: 'string' },
            },
            limit: {
              type: 'integer',
              description: 'Maximum number of results (default: 10)',
            },
          },
        },
      },
      {
        name: 'validate_invoice',
        description: 'Post/validate a draft invoice. Requires approval.',
        inputSchema: {
          type: 'object',
          properties: {
            invoice_id: {
              type: 'integer',
              description: 'Invoice ID to validate',
            },
          },
          required: ['invoice_id'],
        },
      },
      {
        name: 'register_payment',
        description: 'Register a payment for an invoice. Requires approval.',
        inputSchema: {
          type: 'object',
          properties: {
            invoice_id: {
              type: 'integer',
              description: 'Invoice ID',
            },
            amount: {
              type: 'number',
              description: 'Payment amount',
            },
            payment_date: {
              type: 'string',
              description: 'Payment date (YYYY-MM-DD)',
            },
            payment_method: {
              type: 'string',
              description: 'Payment method',
            },
          },
          required: ['invoice_id', 'amount'],
        },
      },
      {
        name: 'get_financial_summary',
        description: 'Get financial summary including receivables, payables, and net position',
        inputSchema: {
          type: 'object',
          properties: {
            period: {
              type: 'string',
              description: 'Period: month, quarter, year',
            },
          },
        },
      },
      {
        name: 'get_partners',
        description: 'Search for customers/suppliers in Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            search_term: {
              type: 'string',
              description: 'Search by name or email',
            },
            limit: {
              type: 'integer',
              description: 'Maximum results (default: 20)',
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'create_invoice':
        const createResult = await createInvoice(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(createResult, null, 2),
            },
          ],
        };

      case 'get_invoices':
        const invoicesResult = await getInvoices(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(invoicesResult, null, 2),
            },
          ],
        };

      case 'validate_invoice':
        const validateResult = await validateInvoice(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(validateResult, null, 2),
            },
          ],
        };

      case 'register_payment':
        const paymentResult = await registerPayment(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(paymentResult, null, 2),
            },
          ],
        };

      case 'get_financial_summary':
        const summaryResult = await getFinancialSummary(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(summaryResult, null, 2),
            },
          ],
        };

      case 'get_partners':
        const partnersResult = await getPartners(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(partnersResult, null, 2),
            },
          ],
        };

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: false,
            error: error.message,
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  log('INFO', 'Odoo MCP server running on stdio');
}

main().catch((error) => {
  log('ERROR', `Server error: ${error.message}`);
  process.exit(1);
});
