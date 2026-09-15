import { stderr } from 'process';

export const logger = {
  debug: (message: string) => {
    if (process.env.DEBUG) stderr.write(`[DEBUG] ${message}\n`);
  },
  info: (message: string) => stderr.write(`[INFO] ${message}\n`),
  warn: (message: string) => stderr.write(`[WARN] ${message}\n`),
  error: (message: string) => stderr.write(`[ERROR] ${message}\n`),
};
