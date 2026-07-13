/**
 * Example TypeScript test file for loop-engineering-template.
 *
 * Demonstrates:
 * - Basic assertion testing
 * - Async testing
 * - Parametrized tests
 * - Mocking patterns
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// --- Example module (normally would import from src/) ---
function greet(name: string): string {
  return `Hello, ${name}!`;
}

function fetchData(success: boolean): Promise<string> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      success ? resolve("data") : reject(new Error("fetch failed"));
    }, 10);
  });
}

class TodoService {
  private items: string[] = [];
  add(item: string): number {
    this.items.push(item);
    return this.items.length;
  }
  getAll(): string[] {
    return [...this.items];
  }
  clear(): void {
    this.items = [];
  }
}

// --- Tests ---

describe("greet", () => {
  it("returns a string", () => {
    const result = greet("World");
    expect(typeof result).toBe("string");
  });

  it("includes the name", () => {
    expect(greet("Alice")).toContain("Alice");
  });

  it("handles empty string", () => {
    expect(greet("")).toBe("Hello, !");
  });

  it("handles special characters", () => {
    expect(greet("Jean-Pierre")).toContain("Jean-Pierre");
  });
});

describe("fetchData", () => {
  it("resolves on success", async () => {
    const data = await fetchData(true);
    expect(data).toBe("data");
  });

  it("rejects on failure", async () => {
    await expect(fetchData(false)).rejects.toThrow("fetch failed");
  });
});

describe("TodoService", () => {
  let service: TodoService;

  beforeEach(() => {
    service = new TodoService();
  });

  it("starts empty", () => {
    expect(service.getAll()).toHaveLength(0);
  });

  it("adds items", () => {
    service.add("item1");
    expect(service.getAll()).toHaveLength(1);
  });

  it("returns count after add", () => {
    expect(service.add("item1")).toBe(1);
    expect(service.add("item2")).toBe(2);
  });

  it("clears all items", () => {
    service.add("item1");
    service.add("item2");
    service.clear();
    expect(service.getAll()).toHaveLength(0);
  });

  it("is isolated between tests (beforeEach works)", () => {
    expect(service.getAll()).toHaveLength(0);
  });
});

describe("mocking example", () => {
  it("can mock a function with vi.fn()", () => {
    const mockFn = vi.fn((x: number) => x * 2);
    expect(mockFn(3)).toBe(6);
    expect(mockFn).toHaveBeenCalledWith(3);
  });
});
