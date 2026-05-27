import chalk from "chalk";
import { setupClient, type ResolveOptions } from "../lib/helius.js";
import { formatSol, formatTimestamp, formatAddress, formatEnumLabel } from "../lib/formatters.js";
import { outputJson, exitWithError, handleCommandError, createSpinner, withRetry, type OutputOptions, type RetryOptions } from "../lib/output.js";
import { validateAddress, validateSignature } from "../lib/validation.js";

interface TxOptions extends OutputOptions, ResolveOptions, RetryOptions {}

export async function txParseCommand(signatures: string[], options: TxOptions = {}): Promise<void> {
  const spinner = createSpinner(options);
  try {
    for (const sig of signatures) {
      const sigErr = validateSignature(sig);
      if (sigErr) exitWithError("INVALID_INPUT", sigErr, undefined, !!options.json);
    }
    const helius = await setupClient(spinner, options, `Parsing ${signatures.length} transaction(s)...`);
    const result = await withRetry(() => helius.enhanced.getTransactions({ transactions: signatures }), options, spinner);
    spinner?.stop();

    if (options.json) {
      outputJson(result);
      return;
    }

    if (!result || (Array.isArray(result) && result.length === 0)) {
      console.log(chalk.yellow("\nNo transactions found."));
      return;
    }

    const txs = Array.isArray(result) ? result : [result];
    for (const tx of txs) {
      console.log(chalk.bold(`\n${"─".repeat(60)}`));
      console.log(`${chalk.gray("Signature:")}    ${chalk.cyan(tx.signature || "N/A")}`);
      console.log(`${chalk.gray("Type:")}         ${chalk.yellow(tx.type ? formatEnumLabel(tx.type) : "Unknown")}`);
      console.log(`${chalk.gray("Source:")}       ${tx.source ? formatEnumLabel(tx.source) : "N/A"}`);
      console.log(`${chalk.gray("Timestamp:")}    ${tx.timestamp ? formatTimestamp(tx.timestamp) : "N/A"}`);
      console.log(`${chalk.gray("Fee:")}          ${tx.fee != null ? formatSol(tx.fee) : "N/A"}`);
      if (tx.description) {
        console.log(`${chalk.gray("Description:")} ${tx.description}`);
      }
      if (tx.nativeTransfers?.length) {
        console.log(chalk.bold("\n  Native Transfers:"));
        for (const t of tx.nativeTransfers) {
          console.log(`    ${t.fromUserAccount || "?"} → ${t.toUserAccount || "?"}: ${formatSol(t.amount)}`);
        }
      }
      if (tx.tokenTransfers?.length) {
        console.log(chalk.bold("\n  Token Transfers:"));
        for (const t of tx.tokenTransfers) {
          console.log(`    ${t.fromUserAccount || "?"} → ${t.toUserAccount || "?"}: ${t.tokenAmount} ${t.mint || ""}`);
        }
      }
    }
    console.log();
  } catch (error) {
    handleCommandError(error, options, spinner);
  }
}

export async function txHistoryCommand(address: string, options: TxOptions & { limit?: string; before?: string; type?: string } = {}): Promise<void> {
  const spinner = createSpinner(options);
  try {
    const addrErr = validateAddress(address);
    if (addrErr) exitWithError("INVALID_ADDRESS", addrErr, undefined, !!options.json);
    const helius = await setupClient(spinner, options, "Fetching transaction history...");
    const params: any = { address };
    if (options.limit) params.limit = parseInt(options.limit, 10);
    if (options.before) params.before = options.before;
    if (options.type) params.type = options.type;
    const result = await withRetry(() => helius.enhanced.getTransactionsByAddress(params), options, spinner);
    spinner?.stop();

    if (options.json) {
      outputJson(result);
      return;
    }

    const txs = Array.isArray(result) ? result : [];
    if (txs.length === 0) {
      console.log(chalk.yellow("\nNo transactions found."));
      return;
    }

    console.log(chalk.bold(`\nTransaction history for ${chalk.cyan(address)}:\n`));
    for (const tx of txs) {
      const sig = tx.signature || "N/A";
      const shortSig = formatAddress(sig);
      const time = tx.timestamp ? formatTimestamp(tx.timestamp) : "N/A";
      const type = tx.type ? formatEnumLabel(tx.type) : "Unknown";
      console.log(`  ${chalk.cyan(shortSig)}  ${chalk.yellow(type.padEnd(16))}  ${chalk.gray(time)}`);
      if (tx.description) {
        console.log(`    ${chalk.gray(tx.description)}`);
      }
    }
    console.log(chalk.gray(`\n  ${txs.length} transaction(s) shown`));
  } catch (error) {
    handleCommandError(error, options, spinner);
  }
}

interface TxTransfersOptions extends TxOptions {
  limit?: string;
  sortOrder?: string;
  mint?: string;
  direction?: string;
  with?: string;
  paginationToken?: string;
  blockTimeGte?: string;
  blockTimeLte?: string;
  commitment?: string;
  solMode?: string;
  amountGte?: string;
  amountLte?: string;
  slotGte?: string;
  slotLte?: string;
}

export async function txTransfersCommand(address: string, options: TxTransfersOptions = {}): Promise<void> {
  const spinner = createSpinner(options);
  try {
    const addrErr = validateAddress(address);
    if (addrErr) exitWithError("INVALID_ADDRESS", addrErr, undefined, !!options.json);

    if (options.commitment && !["finalized", "confirmed"].includes(options.commitment)) {
      exitWithError("INVALID_INPUT", `--commitment must be "finalized" or "confirmed" (got "${options.commitment}")`, undefined, !!options.json);
    }
    if (options.solMode && !["merged", "separate"].includes(options.solMode)) {
      exitWithError("INVALID_INPUT", `--sol-mode must be "merged" or "separate" (got "${options.solMode}")`, undefined, !!options.json);
    }
    if (options.direction && !["in", "out", "any"].includes(options.direction)) {
      exitWithError("INVALID_INPUT", `--direction must be "in", "out", or "any" (got "${options.direction}")`, undefined, !!options.json);
    }
    if (options.sortOrder && !["asc", "desc"].includes(options.sortOrder)) {
      exitWithError("INVALID_INPUT", `--sort-order must be "asc" or "desc" (got "${options.sortOrder}")`, undefined, !!options.json);
    }

    const helius = await setupClient(spinner, options, "Fetching transfers...");

    const limit = options.limit ? Math.min(Math.max(parseInt(options.limit, 10), 1), 100) : 25;
    const sortOrder = options.sortOrder || "desc";
    const direction = options.direction || "any";

    const config: Record<string, unknown> = { direction, limit, sortOrder };
    if (options.mint) config.mint = options.mint;
    if (options.with) config.with = options.with;
    if (options.paginationToken) config.paginationToken = options.paginationToken;
    if (options.commitment) config.commitment = options.commitment;
    if (options.solMode) config.solMode = options.solMode;

    // SDK's TransferComparisonFilter types amount as `number`, so raw u64 values outside JS safe-integer
    // range (>2^53) can't be passed without precision loss. Mirror the MCP handler: surface a clear error
    // rather than silently dropping the filter.
    const parseAmountBound = (raw: string | undefined, label: string): number | undefined => {
      if (raw === undefined) return undefined;
      const n = Number(raw);
      if (!Number.isFinite(n)) {
        exitWithError("INVALID_INPUT", `${label} must be a numeric raw u64 amount (got "${raw}")`, undefined, !!options.json);
      }
      if (!Number.isSafeInteger(n) || n < 0) {
        exitWithError("INVALID_INPUT", `${label}="${raw}" is outside JS safe integer range (>2^53) or negative. Pass a smaller raw amount or filter client-side.`, undefined, !!options.json);
      }
      return n;
    };

    const filters: Record<string, { gte?: number; lte?: number }> = {};
    if (options.blockTimeGte || options.blockTimeLte) {
      filters.blockTime = {};
      if (options.blockTimeGte) filters.blockTime.gte = parseInt(options.blockTimeGte, 10);
      if (options.blockTimeLte) filters.blockTime.lte = parseInt(options.blockTimeLte, 10);
    }
    if (options.slotGte || options.slotLte) {
      filters.slot = {};
      if (options.slotGte) filters.slot.gte = parseInt(options.slotGte, 10);
      if (options.slotLte) filters.slot.lte = parseInt(options.slotLte, 10);
    }
    const aGte = parseAmountBound(options.amountGte, "--amount-gte");
    const aLte = parseAmountBound(options.amountLte, "--amount-lte");
    if (aGte !== undefined || aLte !== undefined) {
      filters.amount = {};
      if (aGte !== undefined) filters.amount.gte = aGte;
      if (aLte !== undefined) filters.amount.lte = aLte;
    }
    if (Object.keys(filters).length > 0) config.filters = filters;

    const result: any = await withRetry(() => (helius as any).getTransfersByAddress(address, config), options, spinner);
    spinner?.stop();

    if (options.json) {
      outputJson(result);
      return;
    }

    const data = result?.data || [];
    if (!Array.isArray(data) || data.length === 0) {
      console.log(chalk.yellow("\nNo transfers found."));
      return;
    }

    const WSOL = "So11111111111111111111111111111111111111112";
    console.log(chalk.bold(`\nTransfers for ${chalk.cyan(address)}:\n`));
    for (const t of data) {
      // SDK omits from/toTokenAccount for native SOL transfers; accept null or undefined from JSON.
      const isSol = t.mint === WSOL && t.fromTokenAccount == null && t.toTokenAccount == null;
      const amount = isSol ? formatSol(Number(t.amount)) : `${t.uiAmount} ${formatAddress(t.mint)}`;
      const symbol = isSol ? "SOL" : "";
      const from = t.fromUserAccount ? formatAddress(t.fromUserAccount) : (t.type === "mint" ? "mint" : "?");
      const to = t.toUserAccount ? formatAddress(t.toUserAccount) : (t.type === "burn" ? "burn" : "?");
      const time = t.blockTime ? formatTimestamp(Number(t.blockTime)) : "N/A";
      console.log(`  ${chalk.yellow((t.type || "transfer").padEnd(10))} ${amount}${symbol ? " " + symbol : ""}`);
      console.log(`    ${from} ${chalk.gray("→")} ${to}`);
      console.log(`    ${chalk.gray("sig:")} ${chalk.cyan(formatAddress(t.signature))}  ${chalk.gray("slot:")} ${t.slot.toString()}  ${chalk.gray(time)}`);
    }
    console.log(chalk.gray(`\n  ${data.length} transfer(s) shown`));
    if (result?.paginationToken) {
      console.log(chalk.gray(`  Next: --pagination-token ${result.paginationToken}`));
    }
  } catch (error) {
    handleCommandError(error, options, spinner);
  }
}

export async function txFeesCommand(options: TxOptions & { accounts?: string } = {}): Promise<void> {
  const spinner = createSpinner(options);
  try {
    const helius = await setupClient(spinner, options, "Fetching priority fee estimate...");
    const params: any = { options: { includeAllPriorityFeeLevels: true } };
    if (options.accounts) {
      params.accountKeys = options.accounts.split(",").map((s: string) => s.trim());
    }
    const result = await withRetry(() => helius.getPriorityFeeEstimate(params), options, spinner);
    spinner?.stop();

    if (options.json) {
      outputJson(result);
      return;
    }

    console.log(chalk.bold("\nPriority Fee Estimates (microlamports per CU):\n"));
    const levels = (result as any)?.priorityFeeLevels;
    if (levels) {
      for (const [level, fee] of Object.entries(levels)) {
        console.log(`  ${chalk.gray(level.padEnd(12))} ${chalk.cyan(String(fee))}`);
      }
    } else {
      console.log(chalk.gray("  No fee data available."));
    }
  } catch (error) {
    handleCommandError(error, options, spinner);
  }
}
