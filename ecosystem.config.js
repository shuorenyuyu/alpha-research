module.exports = {
  apps: [
    {
      name: 'alpha-backend',
      script: '/home/wobbler/alpha-research/start_backend.sh',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'alpha-frontend',
      cwd: '/home/wobbler/alpha-research/dashboard',
      script: 'npm',
      args: 'start',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PORT: 3000
      }
    }
  ]
};
