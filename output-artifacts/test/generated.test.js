const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Generated CPEM contract", function () {
  it("deploys and exposes initial state", async function () {
    const F = await ethers.getContractFactory("ProcessContractP0PurchasingDiamondWithInsuranceContract");
    const c = await F.deploy();
    await c.waitForDeployment();
    expect(await c.state()).to.equal(0n);
  });
});
