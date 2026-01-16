/**
 * Health Check API Route
 *
 * Provides a simple endpoint for checking if the application is running.
 * Useful for load balancers, monitoring, and deployment checks.
 *
 * GET /api/health
 */

import { NextResponse } from 'next/server';
import { logger } from '@/lib/core/logger';

export async function GET() {
  logger.debug('Health check requested');

  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '0.1.0',
    environment: process.env.NODE_ENV,
  };

  logger.info('Health check completed', { status: health.status });

  return NextResponse.json(health);
}
