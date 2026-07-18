import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const desktopDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repoRoot = path.resolve(desktopDir, '..', '..')

describe('Desktop release version metadata', () => {
  it('stays in lockstep with the canonical Hermes package version', () => {
    const pyproject = fs.readFileSync(path.join(repoRoot, 'pyproject.toml'), 'utf8')
    const canonicalVersion = pyproject.match(/^version\s*=\s*"([^"]+)"/m)?.[1]
    const desktopPackage = JSON.parse(
      fs.readFileSync(path.join(desktopDir, 'package.json'), 'utf8')
    ) as { version?: string }
    const packageLock = JSON.parse(
      fs.readFileSync(path.join(repoRoot, 'package-lock.json'), 'utf8')
    ) as { packages?: Record<string, { version?: string }> }

    expect(canonicalVersion).toBeTruthy()
    expect(desktopPackage.version).toBe(canonicalVersion)
    expect(packageLock.packages?.['apps/desktop']?.version).toBe(canonicalVersion)
  })
})
