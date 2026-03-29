module.exports = {
  apps: [
    {
      name: 'cloud-orchestrator',
      script: 'scripts/orchestrator.py',
      interpreter: 'python3',
      args: '--vault ../AI_Employee_Vault --ollama --continuous --interval 60',
      env: {
        PYTHONUNBUFFERED: '1',
        AI_PROVIDER: 'ollama',
        OLLAMA_MODEL: 'qwen2.5:7b'
      },
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      error_file: '../Logs/pm2_orchestrator_error.log',
      out_file: '../Logs/pm2_orchestrator_out.log',
      log_file: '../Logs/pm2_orchestrator_combined.log',
      time: true
    },
    {
      name: 'cloud-watcher-gmail',
      script: 'scripts/gmail_watcher.py',
      interpreter: 'python3',
      args: '../AI_Employee_Vault',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      error_file: '../Logs/pm2_gmail_error.log',
      out_file: '../Logs/pm2_gmail_out.log',
      log_file: '../Logs/pm2_gmail_combined.log',
      time: true
    },
    {
      name: 'cloud-watcher-filesystem',
      script: 'scripts/filesystem_watcher.py',
      interpreter: 'python3',
      args: '../AI_Employee_Vault',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      error_file: '../Logs/pm2_filesystem_error.log',
      out_file: '../Logs/pm2_filesystem_out.log',
      log_file: '../Logs/pm2_filesystem_combined.log',
      time: true
    },
    {
      name: 'cloud-watcher-linkedin',
      script: 'scripts/linkedin_poster.py',
      interpreter: 'python3',
      args: '../AI_Employee_Vault',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      error_file: '../Logs/pm2_linkedin_error.log',
      out_file: '../Logs/pm2_linkedin_out.log',
      log_file: '../Logs/pm2_linkedin_combined.log',
      time: true
    },
    {
      name: 'vault-sync',
      script: 'scripts/vault_sync.py',
      interpreter: 'python3',
      args: '../AI_Employee_Vault --agent cloud-agent',
      env: {
        PYTHONUNBUFFERED: '1',
        AGENT_NAME: 'cloud-agent',
        SYNC_INTERVAL: '300'
      },
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      error_file: '../Logs/pm2_vault_sync_error.log',
      out_file: '../Logs/pm2_vault_sync_out.log',
      log_file: '../Logs/pm2_vault_sync_combined.log',
      time: true
    },
    {
      name: 'health-monitor',
      script: 'scripts/health_monitor.py',
      interpreter: 'python3',
      args: '',
      env: {
        PYTHONUNBUFFERED: '1',
        HEALTH_CHECK_INTERVAL: '60'
      },
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      error_file: '../Logs/pm2_health_monitor_error.log',
      out_file: '../Logs/pm2_health_monitor_out.log',
      log_file: '../Logs/pm2_health_monitor_combined.log',
      time: true
    },
    {
      name: 'gold-weekly-audit',
      script: 'scripts/gold_weekly_audit.py',
      interpreter: 'python3',
      args: '../AI_Employee_Vault',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      restart_delay: 5000,
      max_restarts: 5,
      min_uptime: '10s',
      watch: false,
      cron_restart: '0 7 * * 1', // Every Monday at 7 AM
      error_file: '../Logs/pm2_weekly_audit_error.log',
      out_file: '../Logs/pm2_weekly_audit_out.log',
      log_file: '../Logs/pm2_weekly_audit_combined.log',
      time: true
    }
  ]
};
