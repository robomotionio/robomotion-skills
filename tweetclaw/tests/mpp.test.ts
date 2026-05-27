import { describe, expect, it, vi } from 'vitest';
import { createModuleLoader, initMpp, isCallable, isRecord } from '../src/mpp.js';
import type { ModuleLoader } from '../src/mpp.js';

describe('isRecord', () => {
  it('returns true for plain objects', () => {
    expect.assertions(1);
    expect(isRecord({})).toBe(true);
  });

  it('returns false for null', () => {
    expect.assertions(1);
    expect(isRecord(null)).toBe(false);
  });

  it('returns false for primitives', () => {
    expect.assertions(2);
    expect(isRecord('string')).toBe(false);
    expect(isRecord(42)).toBe(false);
  });

  it('returns true for arrays', () => {
    expect.assertions(1);
    expect(isRecord([])).toBe(true);
  });
});

describe('isCallable', () => {
  it('returns true for functions', () => {
    expect.assertions(1);
    expect(isCallable(() => {})).toBe(true);
  });

  it('returns false for non-functions', () => {
    expect.assertions(3);
    expect(isCallable({})).toBe(false);
    expect(isCallable('string')).toBe(false);
    expect(isCallable(null)).toBe(false);
  });
});

describe('createModuleLoader', () => {
  it('returns a function', () => {
    expect.assertions(1);
    const loader = createModuleLoader();
    expect(typeof loader).toBe('function');
  });

  it('rejects for unavailable modules', async () => {
    expect.assertions(1);
    const loader = createModuleLoader();
    await expect(loader('nonexistent-module-xyz-12345')).rejects.toThrow();
  });
});

function mockLoader(modules: Readonly<Record<string, Record<string, unknown>>>): ModuleLoader {
  return async (name: string): Promise<Record<string, unknown>> => {
    const mod: Record<string, unknown> | undefined = modules[name];
    if (mod === undefined) throw new Error(`Module not found: ${name}`);
    return mod;
  };
}

describe('initMpp', () => {
  it('throws when mppx is not installed', async () => {
    expect.assertions(1);
    const loader = mockLoader({});
    await expect(initMpp('0xabc', loader)).rejects.toThrow('MPP requires mppx package');
  });

  it('throws when viem is not installed', async () => {
    expect.assertions(1);
    const loader = mockLoader({
      'mppx/client': { Mppx: { create: vi.fn() }, tempo: vi.fn() },
    });
    await expect(initMpp('0xabc', loader)).rejects.toThrow('MPP requires viem package');
  });

  it('calls Mppx.create with tempo account when modules are available', async () => {
    expect.assertions(3);
    const mockCreate = vi.fn();
    const mockTempo = vi.fn().mockReturnValue('mock-method');
    const mockPkta = vi.fn().mockReturnValue('mock-account');
    const loader = mockLoader({
      'mppx/client': { Mppx: { create: mockCreate }, tempo: mockTempo },
      'viem/accounts': { privateKeyToAccount: mockPkta },
    });
    await initMpp('0xabc123', loader);
    expect(mockPkta).toHaveBeenCalledWith('0xabc123');
    expect(mockTempo).toHaveBeenCalledWith({ account: 'mock-account' });
    expect(mockCreate).toHaveBeenCalledWith({ methods: ['mock-method'] });
  });

  it('throws when privateKeyToAccount is not a function', async () => {
    expect.assertions(1);
    const loader = mockLoader({
      'mppx/client': { Mppx: { create: vi.fn() }, tempo: vi.fn() },
      'viem/accounts': { privateKeyToAccount: 'not-a-function' },
    });
    await expect(initMpp('0x', loader)).rejects.toThrow('viem missing privateKeyToAccount');
  });

  it('throws when tempo is not a function', async () => {
    expect.assertions(1);
    const loader = mockLoader({
      'mppx/client': { Mppx: { create: vi.fn() }, tempo: 'not-a-function' },
      'viem/accounts': { privateKeyToAccount: vi.fn() },
    });
    await expect(initMpp('0x', loader)).rejects.toThrow('mppx missing tempo');
  });

  it('throws when Mppx is not a record', async () => {
    expect.assertions(1);
    const loader = mockLoader({
      'mppx/client': { Mppx: 'not-an-object', tempo: vi.fn() },
      'viem/accounts': { privateKeyToAccount: vi.fn() },
    });
    await expect(initMpp('0x', loader)).rejects.toThrow('mppx missing Mppx');
  });

  it('throws when Mppx.create is not a function', async () => {
    expect.assertions(1);
    const loader = mockLoader({
      'mppx/client': { Mppx: { create: 'not-a-function' }, tempo: vi.fn() },
      'viem/accounts': { privateKeyToAccount: vi.fn() },
    });
    await expect(initMpp('0x', loader)).rejects.toThrow('mppx Mppx.create is not a function');
  });

  it('uses default loader when none provided', async () => {
    expect.assertions(1);
    await expect(initMpp('0xabc')).rejects.toThrow('MPP requires mppx package');
  });
});
