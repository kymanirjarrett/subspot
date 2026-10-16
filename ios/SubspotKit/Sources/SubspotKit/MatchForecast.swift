import Foundation

/// The three results of a league match, from the home side's perspective.
public enum Outcome: String, Codable, CaseIterable, Sendable {
    case homeWin
    case draw
    case awayWin
}

/// A win/draw/loss forecast for one Premier League match, as served by the Subspot API.
public struct MatchForecast: Codable, Equatable, Sendable {
    public let homeTeam: String
    public let awayTeam: String
    public let homeWin: Double
    public let draw: Double
    public let awayWin: Double

    public enum ValidationError: Error, Equatable {
        case probabilityOutOfRange(Double)
        case probabilitiesDoNotSumToOne(Double)
    }

    /// Tolerance for rounding in probabilities coming off the wire.
    public static let sumTolerance = 1e-6

    public init(homeTeam: String, awayTeam: String, homeWin: Double, draw: Double, awayWin: Double) throws {
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.homeWin = homeWin
        self.draw = draw
        self.awayWin = awayWin
        try validate()
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        homeTeam = try container.decode(String.self, forKey: .homeTeam)
        awayTeam = try container.decode(String.self, forKey: .awayTeam)
        homeWin = try container.decode(Double.self, forKey: .homeWin)
        draw = try container.decode(Double.self, forKey: .draw)
        awayWin = try container.decode(Double.self, forKey: .awayWin)
        try validate()
    }

    public func probability(of outcome: Outcome) -> Double {
        switch outcome {
        case .homeWin: return homeWin
        case .draw: return draw
        case .awayWin: return awayWin
        }
    }

    /// The single most likely result.
    public var mostLikely: Outcome {
        Outcome.allCases.max { probability(of: $0) < probability(of: $1) } ?? .draw
    }

    private func validate() throws {
        for p in [homeWin, draw, awayWin] where !(0.0...1.0).contains(p) {
            throw ValidationError.probabilityOutOfRange(p)
        }
        let total = homeWin + draw + awayWin
        if abs(total - 1.0) > Self.sumTolerance {
            throw ValidationError.probabilitiesDoNotSumToOne(total)
        }
    }
}
