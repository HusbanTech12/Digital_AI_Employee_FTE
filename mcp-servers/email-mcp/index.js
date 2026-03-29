/**
 * Email MCP Server
 * 
 * Model Context Protocol server for sending emails via Gmail or SMTP.
 * Supports both Gmail API and SMTP for flexibility.
 * 
 * Usage:
 *   npx @modelcontextprotocol/sdk email-mcp
 * 
 * Configuration:
 *   Set environment variables or use .env file:
 *   - EMAIL_PROVIDER: 'gmail' or 'smtp'
 *   - GMAIL_CREDENTIALS: Path to Gmail credentials JSON
 *   - SMTP_HOST: SMTP server hostname
 *   - SMTP_PORT: SMTP server port
 *   - SMTP_USER: SMTP username
 *   - SMTP_PASS: SMTP password
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import nodemailer from 'nodemailer';
import { google } from 'googleapis';
import { readFileSync } from 'fs';
import { join } from 'path';

// Configuration
const EMAIL_PROVIDER = process.env.EMAIL_PROVIDER || 'smtp';
const GMAIL_CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS || 'credentials.json';
const SMTP_HOST = process.env.SMTP_HOST || 'smtp.gmail.com';
const SMTP_PORT = parseInt(process.env.SMTP_PORT || '587');
const SMTP_USER = process.env.SMTP_USER || '';
const SMTP_PASS = process.env.SMTP_PASS || '';

// Logging
function log(level, message) {
  const timestamp = new Date().toISOString();
  console.error(`[${timestamp}] [${level}] ${message}`);
}

/**
 * Create Gmail transporter using OAuth2
 */
async function createGmailTransporter() {
  try {
    const credentialsPath = join(process.cwd(), GMAIL_CREDENTIALS_PATH);
    const credentials = JSON.parse(readFileSync(credentialsPath, 'utf-8'));
    
    const oauth2Client = new google.auth.OAuth2(
      credentials.clientId,
      credentials.clientSecret,
      credentials.redirectUris[0]
    );

    // For now, use refresh token if available
    // In production, implement full OAuth flow
    if (process.env.GMAIL_REFRESH_TOKEN) {
      oauth2Client.setCredentials({
        refresh_token: process.env.GMAIL_REFRESH_TOKEN,
      });
    }

    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        type: 'OAuth2',
        user: credentials.authorizedUser?.email || SMTP_USER,
        clientId: credentials.clientId,
        clientSecret: credentials.clientSecret,
        refreshToken: process.env.GMAIL_REFRESH_TOKEN,
        accessToken: await oauth2Client.getAccessToken().then(r => r.token),
      },
    });

    log('INFO', 'Gmail transporter created successfully');
    return transporter;
  } catch (error) {
    log('ERROR', `Failed to create Gmail transporter: ${error.message}`);
    throw error;
  }
}

/**
 * Create SMTP transporter
 */
function createSmtpTransporter() {
  if (!SMTP_USER || !SMTP_PASS) {
    throw new Error('SMTP credentials not configured. Set SMTP_USER and SMTP_PASS environment variables.');
  }

  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: SMTP_PORT,
    secure: SMTP_PORT === 465,
    auth: {
      user: SMTP_USER,
      pass: SMTP_PASS,
    },
  });

  log('INFO', `SMTP transporter created for ${SMTP_HOST}:${SMTP_PORT}`);
  return transporter;
}

/**
 * Get email transporter based on configuration
 */
async function getTransporter() {
  if (EMAIL_PROVIDER === 'gmail') {
    return await createGmailTransporter();
  } else {
    return createSmtpTransporter();
  }
}

/**
 * Send email tool implementation
 */
async function sendEmail(params) {
  const {
    to,
    subject,
    body,
    html,
    cc,
    bcc,
    attachments,
    inReplyTo,
    references,
  } = params;

  if (!to || !subject) {
    throw new Error('Missing required parameters: to, subject');
  }

  log('INFO', `Sending email to: ${to}, subject: ${subject}`);

  try {
    const transporter = await getTransporter();

    const mailOptions = {
      from: SMTP_USER || 'AI Employee',
      to: Array.isArray(to) ? to.join(', ') : to,
      subject: subject,
      text: body || '',
      html: html || body || '',
      cc: cc,
      bcc: bcc,
      attachments: attachments || [],
      inReplyTo: inReplyTo,
      references: references,
    };

    const info = await transporter.sendMail(mailOptions);

    log('INFO', `Email sent successfully. Message ID: ${info.messageId}`);

    return {
      success: true,
      messageId: info.messageId,
      status: 'sent',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    log('ERROR', `Failed to send email: ${error.message}`);
    throw error;
  }
}

/**
 * Draft email tool implementation (save as draft without sending)
 */
async function draftEmail(params) {
  const {
    to,
    subject,
    body,
    html,
    cc,
    bcc,
    attachments,
  } = params;

  if (!to || !subject) {
    throw new Error('Missing required parameters: to, subject');
  }

  log('INFO', `Creating email draft to: ${to}, subject: ${subject}`);

  // For SMTP, we just return the draft content
  // For Gmail API, we could save as actual draft

  const draft = {
    to: Array.isArray(to) ? to.join(', ') : to,
    subject: subject,
    body: body || '',
    html: html || body || '',
    cc: cc,
    bcc: bcc,
    attachments: attachments || [],
    created: new Date().toISOString(),
    status: 'draft',
  };

  log('INFO', 'Email draft created');

  return {
    success: true,
    draft: draft,
    message: 'Email draft created. Review and send when ready.',
  };
}

/**
 * Search emails tool implementation (Gmail only)
 */
async function searchEmails(params) {
  const { query, maxResults = 10 } = params;

  if (EMAIL_PROVIDER !== 'gmail') {
    throw new Error('Search emails is only available with Gmail provider');
  }

  log('INFO', `Searching emails with query: ${query}`);

  try {
    const credentialsPath = join(process.cwd(), GMAIL_CREDENTIALS_PATH);
    const credentials = JSON.parse(readFileSync(credentialsPath, 'utf-8'));
    
    const oauth2Client = new google.auth.OAuth2(
      credentials.clientId,
      credentials.clientSecret,
      credentials.redirectUris[0]
    );

    if (process.env.GMAIL_REFRESH_TOKEN) {
      oauth2Client.setCredentials({
        refresh_token: process.env.GMAIL_REFRESH_TOKEN,
      });
    }

    const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

    const response = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: maxResults,
    });

    const messages = response.data.messages || [];

    log('INFO', `Found ${messages.length} emails`);

    return {
      success: true,
      count: messages.length,
      messages: messages.map(m => ({
        id: m.id,
        threadId: m.threadId,
      })),
    };
  } catch (error) {
    log('ERROR', `Failed to search emails: ${error.message}`);
    throw error;
  }
}

// Create MCP server
const server = new Server(
  {
    name: 'email-mcp',
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
        name: 'send_email',
        description: 'Send an email via Gmail or SMTP. Requires approval for new contacts or bulk sends.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address (or comma-separated list)',
            },
            subject: {
              type: 'string',
              description: 'Email subject line',
            },
            body: {
              type: 'string',
              description: 'Plain text email body',
            },
            html: {
              type: 'string',
              description: 'HTML email body (optional)',
            },
            cc: {
              type: 'string',
              description: 'CC recipients (comma-separated)',
            },
            bcc: {
              type: 'string',
              description: 'BCC recipients (comma-separated)',
            },
            attachments: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  filename: { type: 'string' },
                  path: { type: 'string' },
                  contentType: { type: 'string' },
                },
              },
              description: 'Email attachments',
            },
            inReplyTo: {
              type: 'string',
              description: 'Message ID to reply to',
            },
          },
          required: ['to', 'subject'],
        },
      },
      {
        name: 'draft_email',
        description: 'Create an email draft without sending. Use for review before sending.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject line',
            },
            body: {
              type: 'string',
              description: 'Plain text email body',
            },
            html: {
              type: 'string',
              description: 'HTML email body (optional)',
            },
            cc: {
              type: 'string',
              description: 'CC recipients (comma-separated)',
            },
            bcc: {
              type: 'string',
              description: 'BCC recipients (comma-separated)',
            },
            attachments: {
              type: 'array',
              items: {
                type: 'object',
              },
              description: 'Email attachments',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'search_emails',
        description: 'Search Gmail messages. Only available with Gmail provider.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Gmail search query (e.g., "is:unread", "from:example@gmail.com")',
            },
            maxResults: {
              type: 'integer',
              description: 'Maximum number of results (default: 10)',
            },
          },
          required: ['query'],
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
      case 'send_email':
        const sendResult = await sendEmail(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(sendResult, null, 2),
            },
          ],
        };

      case 'draft_email':
        const draftResult = await draftEmail(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(draftResult, null, 2),
            },
          ],
        };

      case 'search_emails':
        const searchResult = await searchEmails(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(searchResult, null, 2),
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
  log('INFO', 'Email MCP server running on stdio');
}

main().catch((error) => {
  log('ERROR', `Server error: ${error.message}`);
  process.exit(1);
});
